document.getElementById('clearSearchButton').addEventListener('click', function() {
    window.location.href = '/clearSearch';
});

document.getElementById('refreshButton').addEventListener('click', function() {
    window.location.href = '/refresh_returns_and_inventory';
});


document.getElementById('addToJobsButton').addEventListener('click', function() {
    if (confirm('Add the queue to your jobs. The increase inventory operation will execute at 12:00 am ET every night.')) {
        window.location.href = '/create_job';
    }
});

document.getElementById('clearQueueButton').addEventListener('click', function() {
    if (confirm('Are you sure you want to clear the queue?')) {
        window.location.href = '/clearQueue';
    }
});

document.getElementById('downloadPdfButton').addEventListener('click', function() {
    var url = this.getAttribute('data-url');
    window.location.href = url;
});

document.getElementById('downloadSlimButton').addEventListener('click', function() {
    var url = this.getAttribute('data-url');
    window.location.href = url;
});

// Get all the <h3> elements in intro and introAnswers
var introH3s = document.getElementById('intro').querySelectorAll('h3');
var introAnswersH3s = document.getElementById('introAnswers').querySelectorAll('h3');

// Loop through each <h3> element in introAnswers
introAnswersH3s.forEach(function(element, index) {
    // Get the corresponding <h3> element in intro
    var correspondingIntroH3 = introH3s[index];
    // Get the height of the <h3> element in introAnswers
    var height = element.offsetHeight;
    // Set the height of the corresponding <h3> element in intro
    correspondingIntroH3.style.height = height + 'px';
});
