document.addEventListener('DOMContentLoaded', async () => {
    const postsContainer = document.getElementById('posts-container');

    async function fetchPosts() {
        try {
            const response = await fetch('/posts');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const posts = await response.json();
            displayPosts(posts);
        } catch (error) {
            console.error('Error fetching posts:', error);
            postsContainer.innerHTML = '<p>Error loading posts. Please try again later.</p>';
        }
    }

    function displayPosts(posts) {
        postsContainer.innerHTML = ''; // Clear loading message
        if (posts.length === 0) {
            postsContainer.innerHTML = '<p>No posts available yet.</p>';
            return;
        }

        posts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.classList.add('post-card');
            postElement.innerHTML = `
                <h3>${post.username} posted:</h3>
                ${post.snippet_title ? `<h4>${post.snippet_title} (${post.language})</h4>` : ''}
                ${post.code_content ? `<pre><code>${post.code_content}</code></pre>` : ''}
                ${post.caption ? `<p>${post.caption}</p>` : ''}
                <div class="post-meta">
                    <span>${new Date(post.created_at).toLocaleString()}</span>
                    <span>Likes: ${post.likes_count}</span>
                    <span>Comments: ${post.comments_count}</span>
                </div>
                <div class="post-actions">
                    <button class="like-btn" data-post-id="${post.id}">Like</button>
                    <button class="comment-btn" data-post-id="${post.id}">Comment</button>
                </div>
                <div class="comments-section" id="comments-${post.id}" style="display:none;">
                    <h4>Comments:</h4>
                    <div class="comments-list"></div>
                    <textarea class="new-comment-input" placeholder="Add a comment..."></textarea>
                    <button class="submit-comment-btn" data-post-id="${post.id}">Submit Comment</button>
                </div>
            `;
            postsContainer.appendChild(postElement);
        });

        // Add event listeners for like and comment buttons
        postsContainer.querySelectorAll('.like-btn').forEach(button => {
            button.addEventListener('click', handleLike);
        });
        postsContainer.querySelectorAll('.comment-btn').forEach(button => {
            button.addEventListener('click', toggleComments);
        });
        postsContainer.querySelectorAll('.submit-comment-btn').forEach(button => {
            button.addEventListener('click', handleSubmitComment);
        });
    }

    async function handleLike(event) {
        const postId = event.target.dataset.postId;
        try {
            const response = await fetch(`/posts/${postId}/like`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                fetchPosts(); // Refresh posts to update like count
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error liking post:', error);
            alert('An error occurred while liking the post.');
        }
    }

    async function toggleComments(event) {
        const postId = event.target.dataset.postId;
        const commentsSection = document.getElementById(`comments-${postId}`);
        if (commentsSection.style.display === 'none') {
            commentsSection.style.display = 'block';
            await fetchComments(postId, commentsSection.querySelector('.comments-list'));
        } else {
            commentsSection.style.display = 'none';
        }
    }

    async function fetchComments(postId, commentsListElement) {
        try {
            const response = await fetch(`/posts/${postId}/comments`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            const comments = await response.json();
            displayComments(comments, commentsListElement);
        } catch (error) {
            console.error('Error fetching comments:', error);
            commentsListElement.innerHTML = '<p>Error loading comments.</p>';
        }
    }

    function displayComments(comments, commentsListElement) {
        commentsListElement.innerHTML = '';
        if (comments.length === 0) {
            commentsListElement.innerHTML = '<p>No comments yet.</p>';
            return;
        }
        comments.forEach(comment => {
            const commentElement = document.createElement('div');
            commentElement.classList.add('comment-item');
            commentElement.innerHTML = `
                <strong>${comment.username}</strong>: ${comment.content}
                <span>(${new Date(comment.created_at).toLocaleString()})</span>
            `;
            commentsListElement.appendChild(commentElement);
        });
    }

    async function handleSubmitComment(event) {
        const postId = event.target.dataset.postId;
        const commentsSection = document.getElementById(`comments-${postId}`);
        const commentInput = commentsSection.querySelector('.new-comment-input');
        const content = commentInput.value.trim();

        if (!content) {
            alert('Comment cannot be empty.');
            return;
        }

        try {
            const response = await fetch(`/posts/${postId}/comments`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ content })
            });
            const result = await response.json();
            if (response.ok) {
                alert(result.message);
                commentInput.value = ''; // Clear input
                fetchComments(postId, commentsSection.querySelector('.comments-list')); // Refresh comments
                fetchPosts(); // Refresh posts to update comment count
            } else {
                alert(`Error: ${result.message}`);
            }
        } catch (error) {
            console.error('Error submitting comment:', error);
            alert('An error occurred while submitting your comment.');
        }
    }

    fetchPosts();
});