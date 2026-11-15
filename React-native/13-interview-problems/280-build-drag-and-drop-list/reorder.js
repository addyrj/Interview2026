// reorder.js — PURE logic for drag-and-drop reordering (easy to unit test)

// Move item from index `from` to index `to` and return a NEW array
export function moveItem(list, from, to) {
  if (from === to || from < 0 || to < 0 || from >= list.length || to >= list.length) return list; // no-op
  const copy = list.slice();               // never mutate state
  const [item] = copy.splice(from, 1);     // remove dragged item
  copy.splice(to, 0, item);                // insert at the new place
  return copy;
}

// Convert a drag distance (px) to a target index, given row height
export function targetIndex(startIndex, dy, rowHeight, length) {
  const shift = Math.round(dy / rowHeight);                 // how many rows moved
  return Math.min(Math.max(startIndex + shift, 0), length - 1); // clamp inside list
}
