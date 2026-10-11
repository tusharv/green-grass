const prev = document.body.dataset.prev;
const next = document.body.dataset.next;

document.addEventListener("keydown", (event) => {
  const typing = event.target.closest("input, textarea, select");
  if (typing) return;
  if (event.key === "ArrowRight" && next) location.href = next;
  if (event.key === "ArrowLeft" && prev) location.href = prev;
  if (event.key === "Home") location.href = "index.html";
  if (event.key === "End") location.href = "honest.html";
});
