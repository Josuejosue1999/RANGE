function expandButton() {
    var button = document.getElementById('expandButton');
    var contactForm = document.getElementById('contactForm');

    button.style.display = 'none';
    contactForm.classList.remove('hidden');
}
