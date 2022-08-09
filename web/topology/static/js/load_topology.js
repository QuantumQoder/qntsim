$(document).ready(function () {
    $("#submit").click(function () {
        var top_file = $('#topology').val();
        loadTopology(top_file);
    });
});

function loadTopology(topology_file) {
    console.log(topology_file);
    $.ajax({
        type: "GET",
        url: "graph",
        data: {
            topology: topology_file,
        },
        dataType: "json",
        success: function (response) {
            console.log(response);
            $("#response").append(JSON.stringify(response));
        }
    });
}