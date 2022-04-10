function like(postId) {
  const likeButton = document.getElementById(`like-button-${postId}`);
  const likeCount = document.getElementById(`likes-count-${postId}`);

  fetch(`/like_post/${postId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      likeCount.innerHTML = data["likes"];
      if (data["liked"] === true) {
        likeButton.className = "fa-solid fa-heart text-danger";
      } else {
        likeButton.className = "fa-solid fa-heart";
      }
    })
    .catch((e) => alert("Could not like post."));
}
