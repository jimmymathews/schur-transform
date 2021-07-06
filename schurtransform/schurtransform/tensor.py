import numpy as np


class Tensor:
    """
    A data structure for a tensor of type V⊗...⊗V.
    """
    def __init__(self,
        number_of_factors: int=None,
        dimension: int=None,
    ):
        """
        Initializes a zero tensor.

        Args:
            number_of_factors (int):
                Number of tensor factors for the background tensor product vector space.
            dimension (int):
                The dimension of the base vector space.
        """
        self.number_of_factors = number_of_factors
        self.dimension = dimension
        self.data = np.zeros([dimension] * number_of_factors)

    def get_entry_iterator(self):
        """
        An iterator over the entries of the tensor (regarded as a multi-dimensional
        array). This iterator should be used in place of nested for loops, for
        efficiency.

        During iteration, get the current multi-index with ``it.multi_index`` and set
        values with ``it = new_value``.

        Returns:
            iterable:
                The iterator.
        """
        return np.nditer(self.data, flags = ['multi_index'], op_flags=['readwrite'])

    def add(self,
        other_tensor,
        inplace: bool=False,
    ):
        """
        Addition of another tensor.

        Args:
            other_tensor (Tensor):
                The other Tensor object to add.
            inplace (bool):
                If True, adds in place (so that a new Tensor is not returned).

        Returns:
            Tensor:
                The sum (unless ``inplace=True``).
        """
        if inplace:
            self.data = self.data + other_tensor.data
        else:
            tensor = Tensor(
                number_of_factors=self.number_of_factors,
                dimension=self.dimension,
            )
            tensor.data = self.data + other_tensor.data
            return tensor

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
                If True, returns None and modifies this Tensor object in-place.
                Otherwise returns a new Tensor, scaled.

        Returns:
            Tensor:
                The scaled tensor (unless ``inplace=True``).
        """
        if inplace:
            self.data = self.data * amount
        else:
            tensor = Tensor(self.number_of_factors, self.dimension)
            tensor.data = self.data * amount
            return tensor
