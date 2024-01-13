
function closetag(string) {
    let newstring = '';
    if (string.includes('<') && !string.includes('>')) {
        newstring += '>'
    }

    return newstring;
}

console.log(closetag("<dfasdfashda"));


