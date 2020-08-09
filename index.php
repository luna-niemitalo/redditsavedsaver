<?php 
$files = include("./api/getData.php")

?>

<html>
<link rel="stylesheet" type="text/css" href="style.css">
<body>
<div id="masonry">
</div>
<body>
<script src="https://code.jquery.com/jquery-3.5.1.min.js"
    integrity="sha256-9/aliU8dGd2tb6OSsuzixeV4y/faTqgFtohetphbbj0="
    crossorigin="anonymous"></script>
<script type="text/javascript">
    const data = <?php echo($files)?>;
    function imgclick(id) {
        target = "/api/getImage.php?id=" + id;
        window.location.href=target;
    }
    data.forEach(value => {
        const elementString = `
        <figure>
            <figcaption>${value.id}</figcaption>
            <img src="${"/api/getImage.php?id=" + value.id}" onclick="imgclick('${value.id}')">
        </figure>`;
        const element = $.parseHTML( elementString );
        $("#masonry").append(element);
    });
</script>
<html>