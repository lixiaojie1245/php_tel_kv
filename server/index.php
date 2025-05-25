<?php
$dataFile = 'data.json';
$kvStore = [];

// 加载数据
if (file_exists($dataFile)) {
    $json = file_get_contents($dataFile);
    $kvStore = json_decode($json, true) ?? [];
}

// 保存函数
function saveData($data, $file) {
    file_put_contents($file, json_encode($data));
}

// 获取请求方法与路径最后一段
$method = $_SERVER['REQUEST_METHOD'];
$path = basename(parse_url($_SERVER['REQUEST_URI'], PHP_URL_PATH));


// 路由分发
if ($method === 'GET' && $path === 'get') {
    $key = $_GET['key'] ?? '';
    echo isset($kvStore[$key])
        ?  json_encode(['status' => 'OK', 'value' => $kvStore[$key]])
        :  json_encode(['status' => 'NULL']);

} elseif ($method === 'POST' && $path === 'set') {
    $input = json_decode(file_get_contents('php://input'), true);
    if (!isset($input['key'], $input['value'])) {
        http_response_code(400);
        echo  json_encode(['status' => 'ERROR', 'message' => 'Missing key or value']);
        exit;
    }
    $kvStore[$input['key']] = $input['value'];
    saveData($kvStore, $dataFile);
    echo  json_encode(['status' => 'OK']);

} elseif ($method === 'POST' && $path === 'del') {
    $input = json_decode(file_get_contents('php://input'), true);
    $key = $input['key'] ?? '';
    if (isset($kvStore[$key])) {
        unset($kvStore[$key]);
        saveData($kvStore, $dataFile);
        echo  json_encode(['status' => 'OK']);
    } else {
        echo  json_encode(['status' => 'NULL']);
    }

} elseif ($method === 'GET' && $path === 'keys') {
    echo  json_encode(['status' => 'OK', 'keys' => array_keys($kvStore)]);

} else {
	//http_response_code(404);
    echo  json_encode(['status' => 'ERROR', 'message' => 'Unknown endpoint']);
}
?>

