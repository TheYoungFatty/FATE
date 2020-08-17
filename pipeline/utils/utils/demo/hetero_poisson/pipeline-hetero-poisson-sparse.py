#
#  Copyright 2019 The FATE Authors. All Rights Reserved.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import argparse

from pipeline.backend.pipeline import PipeLine
from pipeline.component.dataio import DataIO
from pipeline.component.evaluation import Evaluation
from pipeline.component.hetero_poisson import HeteroPoisson
from pipeline.component.intersection import Intersection
from pipeline.component.reader import Reader
from pipeline.demo.util.demo_util import Config
from pipeline.interface.data import Data


def main(config="../config.yaml"):
    # obtain config
    config = Config(config)
    guest = config.guest
    host = config.host[0]
    arbiter = config.arbiter
    backend = config.backend
    work_mode = config.work_mode

    guest_train_data = {"name": "dvisits_hetero_guest", "namespace": "experiment"}
    host_train_data = {"name": "dvisits_hetero_host", "namespace": "experiment"}

    pipeline = PipeLine().set_initiator(role='guest', party_id=guest).set_roles(guest=guest, host=host, arbiter=arbiter)

    reader_0 = Reader(name="reader_0")
    reader_0.get_party_instance(role='guest', party_id=guest).algorithm_param(table=guest_train_data)
    reader_0.get_party_instance(role='host', party_id=host).algorithm_param(table=host_train_data)

    dataio_0 = DataIO(name="dataio_0", output_format="sparse")

    dataio_0.get_party_instance(role='guest', party_id=guest).algorithm_param(with_label=True,
                                                                              label_name="doctorco",
                                                                              label_type="float")
    dataio_0.get_party_instance(role='host', party_id=host).algorithm_param(with_label=False)

    intersection_0 = Intersection(name="intersection_0")
    hetero_poisson_0 = HeteroPoisson(name="hetero_poisson_0", early_stop="weight_diff", max_iter=20,
                                     alpha=100, batch_size=-1, learning_rate=0.01,
                                     init_param={"init_method": "zeros"},
                                     encrypted_mode_calculator_param={"mode": "fast"}
                                     )

    evaluation_0 = Evaluation(name="evaluation_0", eval_type="regression", pos_label=1)

    pipeline.add_component(dataio_0, data=Data(data=reader_0.output.data))
    pipeline.add_component(intersection_0, data=Data(data=dataio_0.output.data))
    pipeline.add_component(hetero_poisson_0, data=Data(train_data=intersection_0.output.data))
    pipeline.add_component(evaluation_0, data=Data(data=hetero_poisson_0.output.data))

    pipeline.compile()

    pipeline.fit(backend=backend, work_mode=work_mode)

    print (pipeline.get_component("hetero_poisson_0").get_model_param())
    print (pipeline.get_component("hetero_poisson_0").get_summary())
    print (pipeline.get_component("evaluation_0").get_summary())


if __name__ == "__main__":
    parser = argparse.ArgumentParser("PIPELINE DEMO")
    parser.add_argument("-config", default="./config.yaml", type=str,
                        help="config file")
    args = parser.parse_args()
    if args.config is not None:
        main(args.config)
    else:
        main()