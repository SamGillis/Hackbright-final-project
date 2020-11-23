'use strict';

function jumptopageresults(evt) {

    const pageInput = document.querySelector('input[name="page"]');

    let pagesData = $('#pages-java').data('count');

    if (pagesData < pageInput.value) {
        alert('This page does not exist')
        return
    }

    let url = window.location.href;
    let urlComponents = url.split('/');
    url = urlComponents[urlComponents.length - 1];
    urlComponents = url.split("&");
    let temp = urlComponents.pop();
    if (!temp.includes('page')) {
        urlComponents.push(temp);
    }
    url = urlComponents.join('&');
    window.location.href = `/${url}&page=${pageInput.value}`;
}

$('#jumpresults').on('click', jumptopageresults);

$('#jumpcollection').on('click', jumptopageresults);


var seen = {};
$('.lendablefrom').each(function() {
    var txt = $(this).text();
    if (seen[txt])
        $(this).remove();
    else
        seen[txt] = true;
});

var seen = {};
$('.bookincollections').each(function() {
    var txt = $(this).text();
    if (seen[txt])
        $(this).remove();
    else
        seen[txt] = true;
});

var seen = {};
$('.privatecollections').each(function() {
    var txt = $(this).text();
    if (seen[txt])
        $(this).remove();
    else
        seen[txt] = true;
});


