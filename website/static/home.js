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

