from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import super
from builtins import range
from future import standard_library
standard_library.install_aliases()
from future.utils import with_metaclass

from abc import ABCMeta
from abc import abstractmethod

import chainer
from chainer import links as L

from chainerrl.recurrent import RecurrentChainMixin
from chainerrl.links.mlp import MLP


class VFunction(with_metaclass(ABCMeta, object)):

    @abstractmethod
    def __call__(self, x, test=False):
        raise NotImplementedError()


class SingleModelVFunction(
        chainer.Chain, VFunction, RecurrentChainMixin):
    """Q-function with discrete actions.

    Args:
        model (chainer.Link):
            Link that is callable and outputs action values.
    """

    def __init__(self, model):
        super().__init__(model=model)

    def __call__(self, x, test=False):
        h = self.model(x, test=test)
        return h


class FCVFunction(SingleModelVFunction):

    def __init__(self, n_input_channels, n_hidden_layers=0,
                 n_hidden_channels=None):
        self.n_input_channels = n_input_channels
        self.n_hidden_layers = n_hidden_layers
        self.n_hidden_channels = n_hidden_channels

        super().__init__(
            model=MLP(self.n_input_channels, 1,
                      [self.n_hidden_channels] * self.n_hidden_layers),
        )