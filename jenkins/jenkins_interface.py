from workflow import web
from jenkins.job import Job


class JenkinsInterface(object):
    def __init__(self, workflow, web_wrapper=None):
        super(JenkinsInterface, self).__init__()
        self._workflow = workflow
        if not web_wrapper:
            web_wrapper = WebWrapper()

        self._web_wrapper = web_wrapper

    def set_jenkins_url(self, url):
        self._workflow.settings['jenkins_url'] = url
        self._workflow.settings.save()

    def get_all_jobs(self, query=None):
        def _get_jenkins_url():
            jenkins_url = self._workflow.settings.get('jenkins_url')
            if not jenkins_url:
                self._workflow.add_item("No jenkins url set, please set using command: 'jenkins_url'")
                self._workflow.send_feedback()
            return jenkins_url

        def _get_jobs_json():
            jenkins_url = _get_jenkins_url()
            return self._web_wrapper.get("{}/api/json?tree=jobs[name,url,color,description]".format(jenkins_url)).json()['jobs']

        jobs = [Job(data) for data in _get_jobs_json()]
        if query:
            filtered_jobs = self._workflow.filter(query, jobs, lambda x: x.name)
            filtered_jobs.reverse()
            return filtered_jobs
        else:
            return jobs

    def get_failed_jobs(self, query=None):
        all_jobs = self.get_all_jobs(query)
        return [job for job in all_jobs if 'red' in job.status]

    def get_building_jobs(self, query=None):
        all_jobs = self.get_all_jobs(query)
        return [job for job in all_jobs if 'anime' in job.status]


class WebWrapper(object):
    """ Used to better unit test the communication with a Jenkins Server
    """

    def get(self, url, **kwargs):
        return web.get(url, kwargs)