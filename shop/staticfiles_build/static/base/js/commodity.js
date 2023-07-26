const leaveCommentBtn = document.getElementById("leave-comment");
const commentFormExitBtn = document.getElementById("comment-form-exit");
const commentFormWrapper = document.getElementById("comment-form-wrapper");

leaveCommentBtn?.addEventListener("click", e => {
  if(!commentFormWrapper.classList.contains("active"))
    commentFormWrapper.classList.add("active");
});

commentFormExitBtn?.addEventListener("click", e => {
  if(commentFormWrapper.classList.contains("active"))
    commentFormWrapper.classList.remove("active");
});