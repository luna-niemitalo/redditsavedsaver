<?php
// required headers
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Headers: access");
header("Access-Control-Allow-Methods: GET");
header("Access-Control-Allow-Credentials: true");
//header("Content-Type: image/png");

function buildUrl($id) {
    $dir = "./savedImages/";
    //$dir = "../savedImages/";
    //$dir = "/mnt/sbfi01/redditsavedsaver/savedImages/";
    $fileNames = scandir($dir);
    echo($fileNames);
    return $filenames;
    $found = array_values(array_filter($fileNames, function($el) use ($id) {
            return ( strpos($el, $id) !== false );
        }));
    if ($found && count($found) == 1) {
        return $dir . $found[0];
    }

    return "";
}

$id = isset($_GET['id']) ? $_GET['id'] : die();

$url = buildUrl($id);
echo($url);
$fp = fopen($url, 'rb');
header("Content-Length: " . filesize($url));
fpassthru($fp);
exit;
?>
