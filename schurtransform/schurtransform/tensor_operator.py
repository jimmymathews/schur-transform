import numpy as np

from .tensor import Tensor
from .log_formats import colorized_logger
logger = colorized_logger(__name__)


class TensorOperator:
    """
    A data structure for an endomorphism of tensors, a linear transformation, an
    element of End(V⊗...⊗V).
    """
    def __init__(self,
        number_of_factors: int=None,
        dimension: int=None,
        identity: bool=False,
        permutation_inverse=None,
    ):
        """
        Args:
            number_of_factors (int):
                Number of tensor factors for the background tensor product vector space.
            dimension (int):
                The dimension of the base vector space.
            identity (bool):
                If True, initializes the TensorOperator to the identity operator.
            permutation_inverse (list):
                If provided, initializes the TensorOperator to be the operation of
                permutation of the tensor factors, for the inverse of the permutation
                indicated by this list of positive integers (e.g. ``[2, 1, 3]``).
        """
        self.number_of_factors = number_of_factors
        self.dimension = dimension
        self.data = np.zeros(
            [dimension] * (number_of_factors * 2)
        )

        if identity and not permutation_inverse is None:
            logger.error('Provide identity=True or permutation_inverse, not both.')
            return

        n = self.number_of_factors
        if identity:
            it = np.nditer(self.data, flags = ['multi_index'])
            for entry in it:
                index = it.multi_index
                in_index = [index[i] for i in range(n)]
                out_index = [index[i+n] for i in range(n)]
                if(in_index == out_index):
                    self.data[index] = 1.0
        if not permutation_inverse is None:
            it = np.nditer(self.data, flags = ['multi_index'])
            for entry in it:
                index = it.multi_index
                in_index = [index[i] for i in range(n)]
                out_index = [index[i+n] for i in range(n)]
                permuted_in_index = [index[permutation_inverse[i]-1] for i in range(n)]
                if(permuted_in_index == out_index):
                    self.data[index] = 1.0

    def apply(self,
        input_tensor: Tensor=None,
    ):
        """
        Args:
            input_tensor (Tensor):
                The input to which to apply the TensorOperator.

        Returns:
            Tensor:
                Result of application of the TensorOperator linear map.
        """
        if (
            input_tensor.number_of_factors != self.number_of_factors or
            input_tensor.dimension != self.dimension
        ):
            logger.error(
                "input_tensor type (number_of_factors, dimension)=(%s,%s) is not compatible with this operator, expected (%s, %s).",
                str(input_tensor.number_of_factors),
                str(input_tensor.dimension),
                str(self.number_of_factors),
                str(self.dimension),
            )
            return
        output_tensor = Tensor(
            number_of_factors=self.number_of_factors,
            dimension=self.dimension,
        )
        iterator_output = output_tensor.get_entry_iterator()
        for output_entry in iterator_output:
            I = iterator_output.multi_index
            iterator_input = input_tensor.get_entry_iterator()
            accumulator = 0
            for input_entry in iterator_input:
                J = iterator_input.multi_index
                accumulator += self.data[I + J] * iterator_input[0]
            iterator_output[0] = accumulator
        return output_tensor

    def add(self,
        other_operator,
        inplace: bool=False,
    ):
        """
        Args:
            other_operator (TensorOperator):
                Another operator to add in-place.
            inplace (bool):
                If True, adds the other operator in place (so that a new TensorOperator
                is not returned).

        Returns:
            TensorOperator:
                The sum (unless ``inplace=True``, then returns None).
        """
        if inplace:
            self.data = self.data + other_operator.data
        else:
            tensor_operator = TensorOperator(
                number_of_factors=self.number_of_factors,
                dimension=self.dimension,
            )
            tensor_operator.data = self.data + other_operator.data
            return tensor_operator

    def scale_by(self,
        amount: float=None,
        inplace: bool=False,
    ):
        """
        Scalar multiplication, entrywise.

        Args:
            amount (float):
                The scalar to multiply by.
            inplace (bool):
                If True, returns None and modifies this TensorOperator object in-place.
                Otherwise returns a new TensorOperator, scaled.

        Returns:
            TensorOperator:
                The scaled operator (unless ``inplace`` is True, then returns None).
        """
        if inplace:
            self.data = self.data * amount
        else:
            tensor_operator = TensorOperator(self.number_of_factors, self.dimension)
            tensor_operator.data = self.data * amount
            return tensor_operator
