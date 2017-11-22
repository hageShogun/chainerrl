from __future__ import unicode_literals
from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from builtins import *  # NOQA
from future import standard_library
standard_library.install_aliases()

import unittest

import chainer
import chainer.functions as F
from chainer import testing
from chainer.testing import attr
import numpy as np

import chainerrl


@testing.parameterize(
    *testing.product({
        'n_input_channels': [1, 5],
        'action_size': [1, 2],
        'bound_action': [True, False],
        'nonlinearity': ['relu', 'elu'],
        'model_class': [chainerrl.policies.FCDeterministicPolicy],
        'model_kwargs': testing.product({
            'n_hidden_layers': [0, 1, 2],
            'n_hidden_channels': [1, 2],
            'last_wscale': [1, 1e-3],
        }),
    }),
    *testing.product({
        'n_input_channels': [1, 5],
        'action_size': [1, 2],
        'bound_action': [True, False],
        'nonlinearity': ['relu', 'elu'],
        'model_class': [chainerrl.policies.FCBNDeterministicPolicy],
        'model_kwargs': testing.product({
            'n_hidden_layers': [0, 1, 2],
            'n_hidden_channels': [1, 2],
            'normalize_input': [True, False],
            'last_wscale': [1, 1e-3],
        }),
    }),
    *testing.product({
        'n_input_channels': [1, 5],
        'action_size': [1, 2],
        'bound_action': [True, False],
        'nonlinearity': ['relu', 'elu'],
        'model_class': [chainerrl.policies.FCLSTMDeterministicPolicy],
        'model_kwargs': testing.product({
            'n_hidden_layers': [0, 1, 2],
            'n_hidden_channels': [1, 2],
            'last_wscale': [1, 1e-3],
        }),
    })
)
class TestDeterministicPolicy(unittest.TestCase):

    def _test_call(self, gpu):
        # This method only check if a given model can receive random input
        # data and return output data with the correct interface.
        nonlinearity = getattr(F, self.nonlinearity)
        min_action = np.full((self.action_size,), -0.01, dtype=np.float32)
        max_action = np.full((self.action_size,), 0.01, dtype=np.float32)
        model = self.model_class(
            n_input_channels=self.n_input_channels,
            action_size=self.action_size,
            bound_action=self.bound_action,
            min_action=min_action,
            max_action=max_action,
            nonlinearity=nonlinearity,
            **self.model_kwargs,
        )

        batch_size = 7
        x = np.random.rand(
            batch_size, self.n_input_channels).astype(np.float32)
        if gpu >= 0:
            model.to_gpu(gpu)
            x = chainer.cuda.to_gpu(x)
            min_action = chainer.cuda.to_gpu(min_action)
            max_action = chainer.cuda.to_gpu(max_action)
        y = model(x)
        self.assertTrue(isinstance(
            y, chainerrl.distribution.ContinuousDeterministicDistribution))
        a = y.sample()
        self.assertTrue(isinstance(a, chainer.Variable))
        self.assertEqual(a.shape, (batch_size, self.action_size))
        self.assertEqual(chainer.cuda.get_array_module(a),
                         chainer.cuda.get_array_module(x))
        if self.bound_action:
            self.assertTrue((a.data <= max_action).all())
            self.assertTrue((a.data >= min_action).all())

    def test_call_cpu(self):
        self._test_call(gpu=-1)

    @attr.gpu
    def test_call_gpu(self):
        self._test_call(gpu=0)
