# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# coding=utf-8
# Copyright 2018-2022 EVA
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import json

import pandas as pd
from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe

import requests
import pandas as pd
from evadb.catalog.catalog_type import NdArrayType
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.functions.decorators.decorators import forward, setup
from evadb.functions.decorators.io_descriptors.data_types import PandasDataframe


class GenerateImage(AbstractFunction):
    @setup(cacheable=False, function_type="GenerateImage", batchable=False)
    def setup(self):
        pass

    @property
    def name(self) -> str:
        return "GenerateImage"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["command"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["result"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        input_data = df.iloc[0, 0]
        url = "http://localhost:8080/v1/images/generations"
        headers = {
            "Content-Type": "application/json",
        }
        data = {
            "prompt": input_data,
            "size": "256x256",
        }

        response = requests.post(url, headers=headers, json=data)
        response_data = json.loads(response.text)
        # print(response_data)
        # Extract the URL from the parsed response
        url_extracted = response_data["data"][0]["url"]
        df = pd.DataFrame({'result': [url_extracted]})
        # print(df)
        return df
        # return url_extracted
