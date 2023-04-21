const changeText = () => {
    var elem = document.getElementById('genres');
    var values = [];
    for (var option of document.getElementById('genres').options)
    {
        if (option.selected) {
            values.push(option.value);
        }
    }
    document.getElementsByClassName('selected-genres')[0].textContent = values.join('+');
}