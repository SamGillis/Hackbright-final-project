'use strict';

function jumptopageresults(evt) {

    const pageInput = document.querySelector('input[name="page"]');

    let url = window.location.href;
    let urlComponents = url.split('/');
    url = urlComponents[urlComponents.length - 1];
    urlComponents = url.split("&");
    urlComponents.pop();
    url = urlComponents.join('&')
    window.location.href = `/${url}&page=${pageInput.value}`;
}

$('#jumpresults').on('click', jumptopageresults);