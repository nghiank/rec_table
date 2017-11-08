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
}

// Submit post on submit
$('#post-form').on('submit', function(event){
    event.preventDefault();
    var formData = new FormData(this);
    var num = formData.getAll('num');
    var big = formData.getAll('big');
    var small = formData.getAll('small');
    var roll = formData.getAll('roll');
    var x = formData.getAll('x');
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
    $.ajax({
        url: $('#post-form').attr('action'),
        type: 'POST',
        data: formData,
        async: false,
        success: function (data) {
            alert(data)
        },
        cache: false,
        contentType: false,
        processData: false
    });
});
});