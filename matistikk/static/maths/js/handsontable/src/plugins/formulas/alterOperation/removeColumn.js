import {arrayEach} from 'handsontable/helpers/array';
import {cellCoordFactory, isFormulaExpression} from './../utils';
import CellValue from './../cell/value';
import ExpressionModifier from './../expressionModifier';

export const OPERATION_NAME = 'remove_column';

export function operate(start, amount, modifyFormula = true) {
  amount = -amount;

  const {matrix, dataProvider, sheet} = this;
  const translate = [0, amount];
  const indexOffset = Math.abs(amount) - 1;

  let removedCellRef = matrix.removeCellRefsAtRange({column: start}, {column: start + indexOffset});
  let toRemove = [];

  arrayEach(matrix.data, (cell) => {
    arrayEach(removedCellRef, (cellRef) => {
      if (!cell.hasPrecedent(cellRef)) {
        return;
      }

      cell.removePrecedent(cellRef);
      cell.setState(CellValue.STATE_OUT_OFF_DATE);

      arrayEach(sheet.getCellDependencies(cell.row, cell.column), (cellValue) => {
        cellValue.setState(CellValue.STATE_OUT_OFF_DATE);
      });
    });

    if (cell.column >= start && cell.column <= (start + indexOffset)) {
      toRemove.push(cell);
    }
  });

  matrix.remove(toRemove);

  arrayEach(matrix.cellReferences, (cell) => {
    if (cell.column >= start) {
      cell.translateTo(...translate);
    }
  });

  arrayEach(matrix.data, (cell) => {
    const {row: origRow, column: origColumn} = cell;

    if (cell.column >= start) {
      cell.translateTo(...translate);
      cell.setState(CellValue.STATE_OUT_OFF_DATE);
    }

    if (modifyFormula) {
      const {row, column} = cell;
      const value = dataProvider.getSourceDataAtCell(row, column);

      if (isFormulaExpression(value)) {
        const startCoord = cellCoordFactory('column', start);
        const expModifier = new ExpressionModifier(value);

        expModifier.useCustomModifier(customTranslateModifier);
        expModifier.translate({column: amount}, startCoord({row: origRow, column: origColumn}));

        dataProvider.updateSourceData(row, column, expModifier.toString());
      }
    }
  });
}

function customTranslateModifier(cell, axis, delta, startFromIndex) {
  const {start, end, type} = cell;
  const startIndex = start[axis].index;
  const endIndex = end[axis].index;
  const indexOffset = Math.abs(delta) - 1;
  let deltaStart = delta;
  let deltaEnd = delta;
  let refError = false;

  // Mark all cells as #REF! which refer to removed cells between startFromIndex and startFromIndex + delta
  if (startIndex >= startFromIndex && endIndex <= startFromIndex + indexOffset) {
    refError = true;
  }

  // Decrement all cells below startFromIndex
  if (!refError && type === 'cell') {
    if (startFromIndex >= startIndex) {
      deltaStart = 0;
      deltaEnd = 0;
    }
  }

  if (!refError && type === 'range') {
    if (startFromIndex >= startIndex) {
      deltaStart = 0;
    }
    if (startFromIndex > endIndex) {
      deltaEnd = 0;

    } else if (endIndex <= startFromIndex + indexOffset) {
      deltaEnd -= Math.min(endIndex - (startFromIndex + indexOffset), 0);
    }
  }

  if (startIndex + deltaStart < 0) {
    deltaStart -= startIndex + deltaStart;
  }

  return [deltaStart, deltaEnd, refError];
}
