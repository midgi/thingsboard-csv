window.onload = function(){
    var getUrl = window.location;
    const BASE_URL = getUrl .protocol + "//" + getUrl.host ;
    $(".select2-multitag").select2({
        tags: true,
        tokenSeparators: [',', ' '],
        multiple: "multiple"
    });

    $(".datetime").each( (index,el)=> $(el).datetimepicker(
        {format: 'Y-m-d H:i'}
    ));

    let searchParams = new URLSearchParams(window.location.search);
    let host = searchParams.get('host');
    let port = searchParams.get('port');
    let token = searchParams.get('token');

    $("#inputCustomer").change(()=>{
        $("#inputDevice").empty();
        $.get(BASE_URL+"/devices", 
            {
                host: host,
                port: port,
                token: token,
                customer: $("#inputCustomer").val()
            }
        ,function(html) {
                console.log(html);
                $("#inputDevice").append(html);
            }
        );
    });
}