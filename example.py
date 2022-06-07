from nowpipes import Analysis, analysis
from inspect import getfullargspec

# from my_analysis import prepare_data

import my_module

analysis = Analysis()
analysis.add( my_module )
# analysis.run()

deps = analysis._resolve_dependencies()
print( deps )
