// window.onload = function () {
//     setTimeout('myrefresh()', 5000); //指定10秒刷新一次
// }
// function myrefresh() {
//     window.location.reload();
// }

function ChangeUser(uuid) {
    window.location.href = "/index?uuid="+uuid; // 使用相对路径
}
function Logout(){
     window.location.href = "/logout";
}
// 打开和关闭添加用户窗口
function openAddDialog() {
  document.getElementById('addFriendModal').style.display = 'block';
}

function closeAddDialog() {
  document.getElementById('addFriendModal').style.display = 'none';
}

function openDeleteDialog() {
  document.getElementById('deleteFriendModal').style.display = 'block';
}

function closeDeleteDialog() {
  document.getElementById('deleteFriendModal').style.display = 'none';
}