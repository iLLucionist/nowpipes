# NOWPIPES

A python micro-framework for setting up and running a data pipeline.

A quick example is in `example.py` and `my_module.py`.

## Features

### Building a data pipe line using decorators

The `@analysis` decorator is used to build data pipelines. On running the
pipeline, the framework will automatically resolve dependencies and execute the
correct order.

### Automatic dependency resolution

The names of functions that are decorated (see above) are the names of
dependencies. Decorated functions with argument names that correspond to the
names of functions in the data pipeline are dependencies that are automatically
resolved at run time.

Additional parameters can be passed to these piped functions and are collected
in the `**params` dictionary, which is available local in the function.

### Results are automatically collected.

The pipeline will automatically collect result values from each piped function
and they are available after execution in the pipe object. For example, if you
define a pipeline called `mydata` and you have a decorated function `calc`, you
can access return values in `mydata.calc`.

### Adding entire modules

To ease code separation and organization of complex data pipelines, you can
split up the entire pipeline across multiple python modules and you can add
entire modules in one go. The framework will automatically only add decorated
functions (`e.g., @analysis`) to the pipeline and everything will magically
work.

To inspect how the dependencies are internally resolved, you can take a look
at: `_resolve_dependencies()`.

## Planned Features

* There is one nasty bug: don't specify additional arguments to decorated
  functions that are not dependencies. In scanning for dependencies, it will
  not be able to find it and get stuck. If you try to run the data pipeline and
  it hangs, check dependency names (functions on one hand and named arguments
  on the other hand). Additional parameters *must* be specified to the
  `run`-function in your pipeline as additional named optional arguments, e.g.:

```python
    # The pipeline mypipe = Analysis() analysis.add(func1, func2, func3)

    # Either: data.config( param="my parameter value")

    # Or... data.run(..., param="my parameter value")

    # ..somewhere where the funcs are you can then get it @analysis def
    func3(func1, func2, **params): print(params.param)
```

* Be able to dynamically add and remove dependencies. Currently, you cannot
  dynamically (e.g., `ipython`) swap older functions for newer functions in the
  pipeline when they are already defined (they are cached). So if you changed
  functions in the pipeline, you need to reload, reimport the functions and
  redefine the pipeline.

