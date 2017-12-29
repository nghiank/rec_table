$(function() {

isValidNum = (num) => {
    if (num.length == 0) {
        return true;
    }
    if (num.length > 4) {
        return false;
    }
    return /^\d+[xX]*$/.test(num);
};

isValidBigorSmall = (num) => {
    if (num.length == 0) {
        return true;
    }

    if (num.length > 3) {
        return false;
    }
    return /^\d+$/.test(num);
};

isValidRoll = (roll) => {
    if (roll.length == 0) {
        return true;
    }
    var c = roll.toUpperCase();
    return c=='R' || c=='I' || c=='K';
};

isValidX = (x) => {
    if (x.length == 0) {
        return true;
    }
    return x == 'x' || x == 'X'; 
};

showError = (i, str) => {
    alert("Error at row:" + i + ", invalid value of " + str);
};

setLoading = (isLoading) => {
    if (isLoading) {
        $('#loading').show();
    } else {
        $('#loading').hide();
    }
};

getColorText = (expected, predicted) => {
    if (!expected  || expected === predicted) {
        return "<span style='color:green;'>" + predicted +"</span>"
    }
    if (expected.length != predicted.length) {
        return "<span style='color:red;'>" + predicted +"</span>"
    }
    let res = "";
    for(let i = 0; i < expected.length; ++i) {
        const color = expected[i] == predicted[i] ? 'green': 'red';
        res += `<span style='color:${color}'>${expected[i]}</span>`;
    }
    return res;
}

const idPrefix = ['order', 'num', 'big', 'small', 'roll', 'x'];
for(let j = 1 /* skip 'order' */; j < idPrefix.length; ++j) { 
    const prefix = '#' + idPrefix[j];
    for(var i = 0; i < 60; ++i) {
        const id = prefix + (j+1);
        const expected = $(id).attr('expected');
        const predicted = $(id).attr('predicted');
        $(id).html(getColorText(expected, predicted));
    }
}

// Submit post on submit
$('#post-form').on('submit', function(event){
    event.preventDefault();
    var formData = new FormData(this);
    let order = [];
    let num = [];
    let big = [];
    let small = [];
    let roll = [];
    let x = [];
    let allResults = [num, big, small, roll, x, order];
    for(let i = 0; i < idPrefix.length; ++i) {
        const prefix = '#' + idPrefix[i];
        for(let j = 0; j < 60; ++j) {
            const id = prefix + (i+1);
            if (i != 0 ) {
                const expected = $(id).attr('expected');
                allResults[i].push(expected);
            } else {
                allResults[0].push(j);
            }
        }
        formData.append(idPrefix[i], allResults[i]);
    }
    var error = false;
    for(var i = 0; i < num.length; ++i) {
        if (!isValidNum(num[i])) {
            showError(i, 'num:' + num[i]);
            error = true;
            break;
        }
        if (!isValidBigorSmall(big[i])) {
            showError(i, 'big:' + big[i]);
            error = true;
            break;
        }
        if (!isValidBigorSmall(small[i])) {
            showError(i, 'small:' + small[i]);
            error = true;
            break;
        }
        if (!isValidRoll(roll[i])) {
            showError(i, 'roll:' + roll[i]);
            error = true;
            break;
        }
        if (!isValidX(x[i])) {
            showError(i, 'x:' + x[i]);
            error = true;
            break;
        }
    }
    if (error) {
        return;
    }
    setLoading(true);
    $.ajax({
        url: $('#post-form').attr('action'),
        type: 'POST',
        data: formData,
        async: false,
        success: function (data) {
            setLoading(false);
            alert(data)
        },
        error: function() {
            setLoading(false);
            alert("Internal error - Please contact Nghia");
        },
        cache: false,
        contentType: false,
        processData: false
    });
});
});