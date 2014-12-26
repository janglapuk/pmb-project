function updatePaymentCounts(jsonURL) {
    var url = jsonURL;
    data = null
    $.ajax({
        url: url,
        dataType: 'json',
        async: false,
        success: function(response) {
            data = response.data;
        }
    });

    if(data != null) {
            $('#badge-reg-all').text(data.reg.all);
            $('#badge-reg-verified').text(data.reg.verified);
            $('#badge-reg-unverified').text(data.reg.unverified);
            $('#badge-payment-all').text(data.payment.all);
            $('#badge-payment-confirmed').text(data.payment.confirmed);
            $('#badge-payment-unconfirmed').text(data.payment.unconfirmed);
    }
}