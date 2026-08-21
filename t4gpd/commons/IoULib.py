"""
Created on 23 Apr. 2026

@author: tleduc

Copyright 2020-2026 Thomas Leduc

This file is part of t4gpd.

t4gpd is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

t4gpd is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with t4gpd.  If not, see <https://www.gnu.org/licenses/>.
"""

from numpy import array, concatenate, nanmean, ndarray, unique
from sklearn.metrics import confusion_matrix
from t4gpd.commons.IllegalArgumentTypeException import IllegalArgumentTypeException


class IoULib(object):
    """
    classdocs
    """

    def compute_iou(
        y_true: ndarray,
        y_pred: ndarray,
        nodata: int | float | None = None,
    ) -> dict:
        """
        Compute per-class IoU and mean IoU from two categorical arrays.

        Parameters
        ----------
        y_true : ndarray
            Ground-truth labels (any shape, will be flattened).
        y_pred : ndarray
            Predicted labels (same shape as y_true).
        nodata : int | float | None, optional
            Value to ignore in both arrays. Pixels where *either* y_true
            or y_pred equals nodata are excluded from all computations.
            Default is None (no masking).

        Returns
        -------
        dict with keys:
            'iou_per_class' : dict {class_label: iou_value}
            'miou'          : float
            'n_valid'       : int   — number of pixels used
            'n_masked'      : int   — number of pixels excluded (0 if nodata is None)
        """
        if not isinstance(y_true, ndarray):
            raise IllegalArgumentTypeException(y_true, "numpy.ndarray")
        if not isinstance(y_pred, ndarray):
            raise IllegalArgumentTypeException(y_pred, "numpy.ndarray")
        if y_true.shape != y_pred.shape:
            raise IllegalArgumentTypeException(
                (y_true.shape, y_pred.shape), "numpy.ndarray with same shape"
            )

        y_true = y_true.flatten()
        y_pred = y_pred.flatten()

        if nodata is not None:
            valid_mask = (y_true != nodata) & (y_pred != nodata)
            n_masked = int((~valid_mask).sum())
            y_true = y_true[valid_mask]
            y_pred = y_pred[valid_mask]
        else:
            n_masked = 0

        classes = unique(concatenate([y_true, y_pred]))
        cm = confusion_matrix(y_true, y_pred, labels=classes)

        iou_per_class = {}
        for idx, cls in enumerate(classes):
            tp = cm[idx, idx]
            fp = cm[:, idx].sum() - tp
            fn = cm[idx, :].sum() - tp
            denom = tp + fp + fn
            iou_per_class[cls] = tp / denom if denom > 0 else float("nan")

        miou = nanmean(list(iou_per_class.values()))
        return {
            "iou_per_class": iou_per_class,
            "miou": miou,
            "n_valid": len(y_true),
            "n_masked": n_masked,
        }

    def test():
        y_true = array([[0, 1, 2], [1, -1, 0], [2, 0, 1]])  # -1 is nodata
        y_pred = array([[0, 1, 1], [1, 2, -1], [2, 2, 1]])  # -1 is nodata

        result = IoULib.compute_iou(y_true, y_pred, nodata=-1)

        print(f"Mean IoU: {result['miou']:.4f}")
        for cls, iou in result["iou_per_class"].items():
            print(f"  IoU class {cls}: {iou:.4f}")
        print(f"Valid pixels: {result['n_valid']}")
        print(f"Masked pixels: {result['n_masked']}")


# IoULib.test()
