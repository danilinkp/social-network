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

function follow(userId) {
  const followButton = document.getElementById(`follow-button-${userId}`);
  const followCount = document.getElementById(`followers-count-${userId}`);

  fetch(`/follow_user/${userId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      followCount.innerHTML = data["followers"];
      if (data["followed"] === true) {
        followButton.innerHTML   = "Unfollow";
      } else {
        followButton.innerHTML   = "Follow";
      }
    })
    .catch((e) => console.log(e));
}

function follow1(userId) {
  const followButton = document.getElementById(`follow2-button-${userId}`);

  fetch(`/follow_user/${userId}`, { method: "POST" })
    .then((res) => res.json())
    .then((data) => {
      if (data["followed"] === true) {
        followButton.innerHTML   = "Unfollow";
      } else {
        followButton.innerHTML   = "Follow";
      }
    })
    .catch((e) => console.log(e));
}
