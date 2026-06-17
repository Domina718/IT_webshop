document.addEventListener("DOMContentLoaded", function() {

    const stars = document.querySelectorAll('.star-rating span');
    const ratingInput = document.querySelector('input[name="rating"]');

    if(stars.length && ratingInput) {

        function clearStars() {
            stars.forEach(star => {
                star.classList.remove('hovered');
                star.classList.remove('active');
            });
        }

        function paintStars(value, className) {
            clearStars();

            for (let i = 0; i < value; i++) {
                stars[i].classList.add(className);
            }
        }

        stars.forEach(star => {
            star.addEventListener('mouseover', function() {
                let value = parseInt(this.dataset.value);
                paintStars(value, 'hovered');
            });

            star.addEventListener('click', function() {
                let value = parseInt(this.dataset.value);
                ratingInput.value = value;
                paintStars(value, 'active');
            });
        });

        document.querySelector('.star-rating')
        .addEventListener('mouseleave', function() {
            clearStars();

            if (ratingInput.value) {
                paintStars(parseInt(ratingInput.value), 'active');
            }
        });

        if (ratingInput.value) {
            paintStars(parseInt(ratingInput.value), 'active');
        }
    }


    const editBtn = document.getElementById('edit-review-btn');

    if(editBtn) {
        
        editBtn.addEventListener('click', function() {

            document.getElementById('review-display').style.display = 'none';

            document.getElementById('review-form-container').style.display = 'block';
        });
    }

});

