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

        :param number_of_factors:
            Number of tensor factors for the background tensor product vector space.
        :type number_of_factors: int

        :param dimension:
            The dimension of the base vector space.
        :type dimension: int
        """
        self.number_of_factors = number_of_factors
        self.dimension = dimension
        self.data = np.zeros([dimension] * number_of_factors)

    def get_entry_iterator(self):
        """
        An iterator over the entries of the tensor (regarded as a multi-dimensional
        array). This iterator should be used in place of nested ``for`` loops, for
        efficiency.

        During iteration, get the current multi-index with ``it.multi_index`` and set
        values with ``it = new_value``.

        :return:
            The iterator.
        :rtype: iterable
        """
        return np.nditer(self.data, flags = ['multi_index'], op_flags=['readwrite'])

    def add(self,
        other_tensor,
        inplace: bool=False,
    ):
        """
        Addition of another tensor.

        :param other_tensor:
            The other :py:class:`Tensor` object to add.
        :type other_tensor: Tensor

        :param inplace:
            If True, adds in place (so that a new :py:class:`Tensor` is not returned).
        :type inplace: bool

        :return:
            The sum (unless ``inplace=True``, then returns None).
        :rtype: Tensor
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

        :param amount:
            The scalar to multiply by.
        :type amount: float

        :param inplace:
            If True, returns None and modifies this :py:class:`Tensor` object in-place.
            Otherwise returns a new :py:class:`Tensor`, scaled.
        :type inplace: bool

        :return:
            The scaled tensor (unless ``inplace=True``, then returns None).
        :rtype: Tensor
        """
        if inplace:
            self.data = self.data * amount
        else:
            tensor = Tensor(
                number_of_factors=self.number_of_factors,
                dimension=self.dimension,
            )
            tensor.data = self.data * amount
            return tensor
