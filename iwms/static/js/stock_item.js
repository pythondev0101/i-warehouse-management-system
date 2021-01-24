$(document).ready(function(){

    $.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", CSRF_TOKEN);
            }
        }
    });

    var table_uom = $('#tbl_uom_modal').DataTable({
    });

    $("#length, #width, #height").change(function(){
        var length = $("#length").val();
        var width = $("#width").val();
        var height = $("#height").val();
        $("#cbm").val(length*width*height);
    });

    $("#description").change(function(){
        $("#description_plu").val($(this).val());
    });

    $("#unit_id").change(function(){
        var unit_id = $(this).val();
        $("#tbl_uom_line tr").each(function(){
            var uom_id = $(this).find("input").eq(0).val();
            if (unit_id == uom_id){
                $(this).find("td").eq(2).html("<div class='badge badge-primary'>YES</div>");
            }else{
                $(this).find("td").eq(2).html("<div class='badge badge-secondary'>NO</div>");
            }
        });
    });

    $("#btn_add_uom").click(function(){
        $("tr").each(function() {
            var check = $(this).find("input.chkbox").is(':checked');
            if(check){
                var code = $(this).find("td").eq(2).html();
                var description = $(this).find("td").eq(3).html();
                var status = $(this).find("td").eq(4).html();
                var uom_id = $(this).find("td").eq(0).html();
                if (status == 'YES'){
                    status = "<td style='width:150px' class='text-center'><div class='badge badge-success'>ACTIVE</div></td>";
                }else{
                    status = "<td style='width:150px' class='text-center'><div class='badge badge-danger'>INACTIVE</div></td>";
                }
                var default_unit = "<td style='width:150px' class='text-center'><div class='badge badge-secondary'>NO</div></td>";
                var unit = $("#unit_id").val();
                if (!(unit == "")){
                    if (uom_id == unit){
                        default_unit = "<td style='width:150px' class='text-center'><div class='badge badge-primary'>YES</div></td>";
                    }
                }
                var barcode = $("#barcode").val();
                var default_cost= $("#default_cost").val();
                var default_price = $("#default_price").val();

                $('#tbl_uom_line tr:last').after(
                    `<tr>
                        <td style="display:none;"><input name="uoms[]" type="hidden" value="${uom_id}"></input></td>
                        <td style='width:50px'><input class="chkbox" type="checkbox"></td>
                        ${default_unit}
                        ${status}
                        <td class='text-center'>${description}</td>
                        <td class='text-center'>${code}</td>
                    </tr>
                    `
                    );
                    table_uom.row($(this)).remove().draw();
            }
        });
    });

    $("#btn_delete_line").click(function(){
        $("#tbl_uom_line tr").each(function() {
            var check = $(this).find("input.chkbox").is(':checked');
            if (check){
                var status = "NO";
                if ($(this).find("td").eq(3).html() == `<div class="badge badge-success">ACTIVE</div>`){
                    status = "YES";
                }
                var row = table_uom.row.add([
                    $(this).find("input").eq(0).val(),
                    "<input class='chkbox' type='checkbox'>",
                    $(this).find("td").eq(5).html(),
                    $(this).find("td").eq(4).html(),
                    status
                    
                ]);
                table_uom.row(row).column(0).nodes().to$().addClass('myHiddenColumn');
                table_uom.row(row).draw();
                $(this).remove();
            }
        });
    });

    $("#barcode").change(function(){
        var csrf_token = "{{ csrf_token() }}";
        var barcode = $("#barcode").val();

        $.ajax({
            url: "/iwms/_barcode_check",
            type: "POST",
            dataType: "json",
            data: JSON.stringify({'barcode': barcode}),
            contentType: "application/json; charset=utf-8",
            success: function(data) {
                if(data.result == 1){
                    $("#barcode-invalid-feedback").text("Please provide a valid barcode");
                    document.getElementById("barcode-invalid-feedback").style.display = "none";
                    document.getElementById("barcode-valid-feedback").style.display = "block";
                }else{
                    $("#barcode-invalid-feedback").text("Barcode is already taken.");
                    document.getElementById("barcode-valid-feedback").style.display = "none";
                    document.getElementById("barcode-invalid-feedback").style.display = "block";
                }
            }
        });
    });


});

(function() {
    var fixed_footer = document.getElementById('chkbox_fixed_footer');
    setTimeout(function() {
      fixed_footer.click();
    }, 100);
  })();