import os
import sys
import logging

import xml.dom.minidom
import xml.etree.ElementTree as eT

from bkr.client.task_watcher import watch_tasks
from bkr.client import BeakerCommand, BeakerWorkflow, BeakerJob, \
    BeakerRecipeSet, BeakerRecipe
from bkr.common.hub import HubProxy
from bkr.common.pyconfig import PyConfigParser

LOG = logging.getLogger(__name__)

BEAKER_CONF = \
    (os.environ.get('BEAKER_CONF', '/etc/beaker/client.conf'))


class BkrConn(object):
    """
        Make connection to Beaker
    """
    enabled = True
    doc = xml.dom.minidom.Document()

    def __init__(self, logger=None, conf=None, **kwargs):
        self.conf = PyConfigParser()
        default_config = os.path.expanduser(BEAKER_CONF)
        self.conf.load_from_file(default_config)
        self.hub = HubProxy(logger=logger, conf=self.conf, **kwargs)


class BkrFactory(BkrConn):
    """
        Simple way to provision a job to the Beaker scheduler
    """
    def __init__(self, *args, **kwargs):
        super(BkrFactory, self).__init__(*args, **kwargs)

    def provision(self, *args, **kwargs):
        """
            provision resources in Beaker
        """
        # Break down kwargs for debug, dryrun, wait, and recipesets
        debug = kwargs.get("debug", False)
        dryrun = kwargs.get("dryrun", False)
        wait = kwargs.get("wait", False)
        recipesets = kwargs.get("recipesets", [])

        # Create Job
        job = BeakerJob(*args, **kwargs)

        # Add All Host Requirements
        for recipeset in recipesets:
            kwargs = self.create_recipesets(recipeset, **kwargs)
            family = kwargs.get("family", None)
            distro = kwargs.get("distro", None)
            task_params = kwargs.get("taskparam", [])
            arch = kwargs.get("arch", None)
            ks_meta = kwargs.get("ks_meta", "")
            method = kwargs.get("method", "nfs")
            priority = kwargs.get("priority", "Normal")

            # Tasks and harnesses
            if 'restraint' in ks_meta:
                requested_tasks = \
                    [{'arches': [], 'name': '/restraint/reservesys'}]
                kwargs.update({'repo': ['http://file.bos.redhat.com/'
                                        '~bpeck/restraint/rhel$releasever/']})
            else:
                requested_tasks = \
                    [{'arches': [], 'name': '/distribution/reservesys'}]

            # Update defaults
            kwargs.update({"method": method})
            kwargs.update({"priority": priority})

            # Must have family or distro
            if not family and not distro and not arch:
                sys.stderr.write("No Family or Distro and arch specified\n")
                sys.exit(1)

            if not requested_tasks:
                sys.stderr.write("You must specify a task to run\n")
                sys.exit(1)

            # Create Workflow
            wrkflow = BeakerWorkflow('BeakerWorkflow')

            # Create Base Recipe
            recipe_template = BeakerRecipe(*args, **kwargs)

            # Add Distro Requirements
            recipe_template.addBaseRequires(*args, **kwargs)
            arch_node = self.doc.createElement('distro_arch')
            arch_node.setAttribute('op', '=')
            arch_node.setAttribute('value', arch)
            recipe_set = BeakerRecipeSet(**kwargs)
            if wrkflow.multi_host:
                for i in range(self.n_servers):
                    recipe_set.addRecipe(wrkflow.processTemplate(
                        recipe_template,
                        requested_tasks,
                        taskParams=task_params,
                        distroRequires=arch_node,
                        role='SERVERS',
                        **kwargs))
                for i in range(self.n_clients):
                    recipe_set.addRecipe(wrkflow.processTemplate(
                        recipe_template,
                        requested_tasks,
                        taskParams=task_params,
                        distroRequires=arch_node,
                        role='CLIENTS',
                        **kwargs))
            else:
                recipe_set.addRecipe(wrkflow.processTemplate(
                    recipe_template,
                    requested_tasks,
                    taskParams=task_params,
                    distroRequires=arch_node,
                    **kwargs))
            job.addRecipeSet(recipe_set)

        # jobxml
        jobxml = job.toxml(**kwargs)

        if debug:
            LOG.debug(jobxml)

        self.submitted_jobs = []
        is_failed = False

        if not dryrun:
            try:
                self.submitted_jobs.append(self.hub.jobs.upload(jobxml))
                LOG.info("Submitted: %s" % self.submitted_jobs)
                return self.submitted_jobs
            except (KeyboardInterrupt, SystemExit):
                raise
            except Exception, ex:
                is_failed = True
                sys.stderr.write('Exception: %s\n' % ex)
            if wait:
                is_failed |= watch_tasks(self.hub, self.submitted_jobs)
        sys.exit(is_failed)

    def create_recipesets(self, recipeset, **kwargs):
        kwargs = {}
        for key, values in recipeset.iteritems():
            kwargs.update({key: values})
        return kwargs

    def check_jobs(self, jobs):
        """
            Get state of a job in Beaker
        """
        results = {}
        resources = []
        bkrcmd = BeakerCommand('BeakerCommand')
        bkrcmd.check_taskspec_args(jobs)
        for task in jobs:
            myxml = self.hub.taskactions.to_xml(task)
            myxml = myxml.encode('utf8')
            LOG.debug(xml.dom.minidom.parseString(myxml)
                         .toprettyxml(encoding='utf8'))
            root = eT.fromstring(myxml)
            # TODO: Using getiterator() since its backward compatible
            # with Python 2.6
            # This is deprectated in 2.7 and we should be using iter()
            for job in root.getiterator('job'):
                results.update({'job_id': job.get('id'),
                                'results': job.get('result')})
            for recipe in root.getiterator('recipe'):
                resources.append({'family': recipe.get('family'),
                                  'distro': recipe.get('distro'),
                                  'arch': recipe.get('arch'),
                                  'variant': recipe.get('variant'),
                                  'system': recipe.get('system'),
                                  'status': recipe.get('status'),
                                  'result': recipe.get('result')})
                results.update({'resources': resources})
        return results

    def cancel_jobs(self, jobs, msg):
        """
            Cancel job in Beaker
        """
        for task in jobs:
            self.hub.taskactions.stop(task, 'cancel', msg)
            LOG.info("Cancel job %s in Beaker" % task)