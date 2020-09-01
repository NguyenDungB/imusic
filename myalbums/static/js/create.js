let select2 = $(".select2");

        select2.select2({
            placeholder: "Select artists",
            theme: 'bootstrap4',
            width: 'style',
            tags: true,
        });

        select2.on('select2:select', function (e) {
            let elm = e.params.data.element;
            $elm = jQuery(elm);
            $t = jQuery(this);
            $t.append($elm);
            $t.trigger('change.select2');
        });

        $('#thumbnailFile').change(function () {
            if (this.files && this.files[0]) {
                let reader = new FileReader();

                reader.onload = function (e) {
                    $('.upload-image svg').remove();
                    $('.upload-image img').remove();
                    $('.upload-image').prepend('<img src="' + e.target.result + '" alt="" style="width: 100%"/>');
                };
                reader.readAsDataURL(this.files[0]);
            }
        });

        function _(el) {
            return document.getElementById(el);
        }

        let form = $('form');

        form.submit(function (e) {
            e.preventDefault();

            $(this).find('button[type=submit]').attr('disabled', true);
            $(this).find('.lds-ellipsis').css('display', "block");

            $.ajax({
                url: $(this).attr('action'),
                type: 'post',
                datatype: 'json',
                data: new FormData(this),
                contentType: false,
                processData: false,
                success: function (data) {
                    form.find('button[type=submit]').attr('disabled', false);
                    form.find('.lds-ellipsis').css('display', "none");

                    if (data.status === 'validation' || data.status === 'error') {
                        $.each(data.message, function (index, message) {
                            toastr.warning(message);
                        });
                        toastr.options = {
                            "positionClass": "toast-bottom-right",
                            "timeOut ": 30,
                        };
                    } else if (data.status === true) {

                        toastr.options = {
                            "positionClass": "toast-bottom-right",
                        };
                        toastr.success(data.message);

                        setTimeout(function () {
                            window.location.href = data.redirect;
                        }, 2000);
                    }
                }, error: function (err) {
                    console.log(err.data);
                    form.find('.lds-ellipsis').css('display', "none");
                    form.find('button[type=submit]').attr('disabled', false);
                }
            });
        })
