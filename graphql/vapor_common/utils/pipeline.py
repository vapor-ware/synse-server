#!/usr/bin/env python
""" Vapor Common Job Pipeline

The pipeline here is intended to be used for running bootstrap workflows
for containers on startup.

    Author: Erick Daniszewski
    Date:   7 Feb 2017
    
    \\//
     \/apor IO
"""
import logging


logger = logging.getLogger(__name__)


class Stage(object):
    """ Represents a single job stage in the pipeline.
    """
    def __init__(self, name, fn, fnargs=None, fnkwargs=None, required=True):
        self.name = name
        self.fn = fn
        self.fnargs = fnargs or []
        self.fnkwargs = fnkwargs or {}
        self.required = required

        self.res = None
        self.complete = False

    def execute(self):
        """ Execute the callable for this stage.
        """
        logger.info('* Executing Stage "{}" (required: {})'.format(self.name, self.required))
        try:
            self.res = self.fn(*self.fnargs, **self.fnkwargs)
        except:
            if self.required:
                raise
            else:
                logger.warning(
                    'Stage "{}" failed but not required - continuing to next stage.'.format(self.name)
                )

        self.complete = True


class Pipeline(object):
    """ A job pipeline which runs jobs sequentially, where each job (Stage) can be
    configured with different behaviors.
    """
    def __init__(self):
        self.stages = []

    @property
    def is_complete(self):
        """ Check if all of the stages in the pipeline have completed.

        Returns:
            bool: True if the pipeline is complete; False otherwise
        """
        return all([stage.complete for stage in self.stages])

    def run(self):
        """ Run the pipeline.
        """
        for stage in self.stages:
            stage.execute()

    def add_stage(self, name, fn, fnargs=None, fnkwargs=None, required=True):
        """ Add a new stage to the pipeline.

        The stage is added to the end of the pipeline.

        Args:
            name (str): the name of the pipeline stage.
            fn (callable): the function which will be executed during this stage.
            fnargs (list): any args to pass to the function. (default: None)
            fnkwargs (dict): any kwargs to pass to the function. (default: None)
            required (bool): a flag which, when True, indicates that the pipeline
                will fail at this stage if the stage is unable to successfully
                complete. When False, the stage can fail and the pipeline will
                continue on to the next stage.
        """
        self.stages.append(Stage(
            name=name,
            fn=fn,
            fnargs=fnargs,
            fnkwargs=fnkwargs,
            required=required
        ))
