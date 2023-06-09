# Copyright (c) Meta Platforms, Inc. and affiliates.
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

import abc
from typing import Callable

from opacus.optimizers import DPOptimizer


class IAccountant(abc.ABC):
    @abc.abstractmethod
    def __init__(self):
        pass

    @abc.abstractmethod
    def step(self, *, noise_multiplier: float, sample_rate: float):
        """
        Signal one optimization step

        Args:
            noise_multiplier: Current noise multiplier
            sample_rate: Current sample rate
        """
        pass

    @abc.abstractmethod
    def get_epsilon(self, delta: float, *args, **kwargs) -> float:
        """
        Return privacy budget (epsilon) expended so far.

        Args:
            delta: target delta
            *args: subclass-specific args
            **kwargs: subclass-specific kwargs
        """
        pass

    @abc.abstractmethod
    def __len__(self) -> int:
        """
        Number of optimization steps taken so far
        """
        pass

    @classmethod
    @abc.abstractmethod
    def mechanism(cls) -> str:
        """
        Accounting mechanism name
        """
        pass

    def get_optimizer_hook_fn(
        self, sample_rate: float
    ) -> Callable[[DPOptimizer], None]:
        """
        Returns a callback function which can be used to attach to DPOptimizer
        Args:
            sample_rate: Expested samping rate used for accounting
        """

        def hook_fn(optim: DPOptimizer):
            # This works for Poisson for both single-node and distributed
            # The reason is that the sample rate is the same in both cases (but in
            # distributed mode, each node samples among a subset of the data)
            self.step(
                noise_multiplier=optim.noise_multiplier,
                sample_rate=sample_rate * optim.accumulated_iterations,
            )

        return hook_fn
