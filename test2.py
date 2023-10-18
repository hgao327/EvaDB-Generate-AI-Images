from collections import OrderedDict

import pandas as pd

from evadb.functions.abstract.pytorch_abstract_function import (
    PytorchAbstractClassifierFunction,
)
from evadb.utils.generic_utils import try_to_import_torch, try_to_import_torchvision
import pandas as pd


class ReturnOneFunction(PytorchAbstractClassifierFunction):

    # Setup function
    @setup(cacheable=True, function_type="custom", batchable=True)
    def setup(self):
        pass

    # Forward function
    @forward(
        input_signatures=[],  # No input
        output_signatures=[
            PandasDataframe(
                columns=["result"],
                column_types=[NdArrayType.INT32],
                column_shapes=[(1,)]
            )
        ]
    )
    def forward(self) -> pd.DataFrame:
        return pd.DataFrame({"result": [1]})
