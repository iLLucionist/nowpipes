from inspect import getmembers, isfunction, getfullargspec
from types import ModuleType
from functools import wraps
from copy import deepcopy
from box import Box
from timeit import timeit

# TODO: Refactor Analysis to Pipeline


def module_to_dict(module): return dict(getmembers(module, isfunction))


def isanalysis(x):
    """Check if an object is an analysis by simply checking if an attribute
    exists."""
    return hasattr(x, 'analysis')


class Pipeline:
    def __init__(self):
        """Initialize the primary state variables of the pipeline. _analyses
        contains the piped functions themselves which do the heavy lifting.
        These are specified by the user. _results contains the output that
        those functions in _analyses produce. _dependencies are a simple dict
        that, per analysis function, store their dependencies. _config simply
        contains configuration options that users may specify using config()"""

        self._analyses = {}
        self._results = {}
        self._dependencies = {}
        self._config = {}

    def _getresults(self, key):
        """Helper function to see if a particular _results entry exists.
        If not, raise error. If it exists, return it."""

        if key in self._results.keys():
            return self._results[key]
        else:
            raise KeyError(f'No results found for analysis "{key}".' +
                           ' Have you defined or run the analysis?')

    def __getitem__(self, key):
        """Retrieve item from _results"""
        return self._getresults(key)

    def __getattr__(self, key):
        """Retrieve item from _results"""
        return self._getresults(key)

    def add(self, *args):
        for a in args:
            if isinstance(a, ModuleType):
                self._add_module(a)
            elif isfunction(a):
                self._add_function(a)

    def config(self, **kwargs):
        self._config = self._config | kwargs

    def run(self, analysis=None, verbose=False, indent=0, run_once=(),
            **params):

        cumtime = 0
        indent = indent * '  '
        deps = self._resolve_dependencies()

        if verbose is True:
            print('Running...'.ljust(70), end='\r')

        for i, name in enumerate(deps):
            if name in run_once:
                if name in self._results:
                    print(f'Already run {name}, skipping...')
                    continue
            if verbose is True:
                print(f'{indent}Running {name}...'.ljust(40), end='\r')
            xtime = timeit(lambda: self._run_analysis(
                name, **params), number=1)
            cumtime += xtime
            if verbose is True:
                print(f'{indent}{name}:'.ljust(40) +
                      f'{xtime:.{2}f}s, total: {cumtime:.{2}f}s\n', end='\r')
        else:
            if verbose is True:
                print(f'{indent}DONE! Total time: {cumtime:.{2}f} seconds')

    def _run_analysis(self, name, **params):
        deps = {k: self._results[k] for k in self._dependencies[name]}
        args = deps | self._config | params

        results = self._analyses[name](**args)

        if isinstance(results, dict):
            results = Box(results)

        self._results[name] = results

    def _add_dependencies(self, name, dependencies):
        self._dependencies[name] = dependencies

    def _add_module(self, mod):
        to_add = filter(lambda kv: isanalysis(kv[1]),
                        module_to_dict(mod).items())

        for _, func in to_add:
            self._add_function(func)

    def _add_function(self, func):
        if isanalysis(func) is False:
            raise ValueError('You are trying to add a non-analysis.')
        name = func.__name__
        self._analyses[name] = func

        dependencies = getattr(self._analyses[name], 'dependencies')
        self._add_dependencies(name, dependencies)

    def _resolve_dependencies(self):
        """Resolve execution order of analyses.

        This resolution algorithm is deterministic. Per iteration pass, it
        determines which dependency is not dependent on other dependencies. It
        then pushes itself onto the resolution stack (stack), removes itself
        from all other dependencies that do depend on this dependency, and
        finally removes itself completely as a dependency itself from the
        dependencies stack. The algorithm keeps going until there are no
        dependencies left to process.
        """

        deps = deepcopy(self._dependencies)
        stack = []

        # Keep going until no dependencies left
        while(len(deps) > 0):
            # Find the dependencies that have no other dependencies
            for resolve, _ in list(filter(lambda kv: len(kv[1]) == 0, deps.items())):
                # Push that depdency onto the resolution stack
                stack.append(resolve)
                for _, v in deps.items():
                    # Remove itself from all other dependencies that depend
                    # on this dependency
                    if resolve in v:
                        v.remove(resolve)
                # Remove itself as a dependency
                del deps[resolve]

        return stack


def pipe(func):
    """Only attaches the 'analysis' attribute to provided object. This is used
    by the Pipeline class to determine which objects to add and which to not
    add in add(). That is, only objects that have the attribute 'analysis' will
    be added to the pipeline. The rest will be ignored. Finally, this function
    also sets the argument names of the original function that is decorated as
    dependencies for that function. Thus, the argument names are yet other
    functions in the pipeline that Pipeline will execute and gather the results
    from before running this function. The output of the other dependency
    functions are provided as input parameters for this original function."""
    if callable(func) is False:
        raise TypeError('You are trying to decorate an object as a pipe ' +
                        'for a Pipeline, but the object is not callable!')

    @wraps(func)
    def inner(*args, **kwargs):
        return func(*args, **kwargs)

    setattr(inner, 'analysis', True)
    setattr(inner, 'dependencies', getfullargspec(func).args)

    return inner
