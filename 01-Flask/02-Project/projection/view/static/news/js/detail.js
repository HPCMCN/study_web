function getCookie(name) {
    var r = document.cookie.match("\\b" + name + "=([^;]*)\\b");
    return r ? r[1] : undefined;
}


$(function () {

    // 打开登录框
    $('.comment_form_logout').click(function () {
        $('.login_form_con').show();
    });

    // 收藏
    $(".collection").click(function () {
        var new_id = $(".collection").attr("new_id");
        var action = "collect";
        var params = {
            "new_id": new_id,
            "action": action
        };
        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (response) {
                if (response.errno == "0") {
                    $(".collection").hide();
                    $(".collected").show();
                } else if (response.errno == "4102") {
                    $(".login_form_con").show();
                } else {
                    alert(response.errmsg);
                }

            }

        });
    });

    // 取消收藏
    $(".collected").click(function () {
        var new_id = $(".collected").attr("new_id");
        var action = "cancel_collect";
        var params = {
            "new_id": new_id,
            "action": action
        };
        $.ajax({
            url: "/news/news_collect",
            type: "post",
            contentType: "application/json",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            success: function (response) {
                if (response.errno == "0") {
                    $(".collection").show();
                    $(".collected").hide();
                } else if (response.errno == "4102") {
                    $(".login_form_con").show();
                } else {
                    alert(response.errmsg);
                }

            }
        })

    });

    // 评论提交
    $(".comment_form").submit(function (e) {
        e.preventDefault()
        var new_id = $(this).attr("new_id");
        var comment = $(".comment_input").val();
        if (!comment) {
            alert("评论不能为空！");
            return
        }
        var params = {
            "new_id": new_id,
            "comment": comment
        };
        $.ajax({
            url: "/news/news_comment",
            type: "post",
            headers: {
                "X-CSRFToken": getCookie("csrf_token")
            },
            data: JSON.stringify(params),
            contentType: "application/json",
            success: function (resp) {
                if (resp.errno == "0") {
                    $(".comment_form").blur();
                    $(".comment_sub").val();
                    location.reload()
                } else if (resp.errno == "4102") {
                    $(".login_form_con").show();
                    return
                }else {
                    alert(resp.errmsg);
                    return
                }
            },

        });

    });

    $('.comment_list_con').delegate('a,input', 'click', function () {

        var sHandler = $(this).prop('class');

        if (sHandler.indexOf('comment_reply') >= 0) {
            $(this).next().toggle();
        }

        if (sHandler.indexOf('reply_cancel') >= 0) {
            $(this).parent().toggle();
        }
        // 前端逻辑实现 , 实现点赞逻辑
        if(sHandler.indexOf('comment_up')>=0)
{
    var $this = $(this);
    var action = "add"
    if(sHandler.indexOf('has_comment_up')>=0)
    {
        // 如果当前该评论已经是点赞状态，再次点击会进行到此代码块内，代表要取消点赞
        action = "remove"
    }

    var comment_id = $(this).attr("data-commentid")
    var news_id = $(this).attr("data-newsid")
    var params = {
        "comment_id": comment_id,
        "action": action,
        "news_id": news_id
    }

    $.ajax({
        url: "comment_like",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 更新点赞按钮图标
                if (action == "add") {
                    // 代表是点赞
                    $this.addClass('has_comment_up')
                }else {
                    $this.removeClass('has_comment_up')
                }
            }else if (resp.errno == "4102"){
                $('.login_form_con').show();
            }else {
                alert(resp.errmsg)
            }
        }
    })
}

        if (sHandler.indexOf('reply_sub') >= 0) {
            var $this = $(this)
            var new_id = $this.parent().attr("new_id")
            var parent_id = $this.parent().attr("comment_id")
            var comment = $this.prev().val()
            if (!comment){
                alert("回复不能为空！")
                return
            }
            var params = {
                "new_id": new_id,
                "parent_id": parent_id,
                "comment": comment
            }
            $.ajax({
                url: "/news/news_comment",
                type: "post",
                contentType: "application/json",
                headers: {
                    "X-CSRFToken": getCookie("csrf_token")
                },
                data: JSON.stringify(params),
                success: function(response){
                    if (response.errno=="0"){
                        location.reload()
                        var comment = response.data
                    }else if (response.errno == "4102"){
                        $(".login_form_con").show();
                    }else{
                        alert(response.errmsg)
                    }
                }
            })
        }
    });

    // 关注当前新闻作者
    $(".focus").click(function () {
    var user_id = $(this).attr('data-userid')
    var params = {
        "action": "follow",
        "user_id": user_id
    }
    $.ajax({
        url: "/news/followed_user",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 关注成功
                var count = parseInt($(".follows b").html());
                count++;
                $(".follows b").html(count + "")
                $(".focus").hide()
                $(".focused").show()
            }else if (resp.errno == "4101"){
                // 未登录，弹出登录框
                $('.login_form_con').show();
            }else {
                // 关注失败
                alert(resp.errmsg)
            }
        }
    })
})

// 取消关注当前新闻作者
$(".focused").click(function () {
    var user_id = $(this).attr('data-userid')
    var params = {
        "action": "unfollow",
        "user_id": user_id
    }
    $.ajax({
        url: "/news/followed_user",
        type: "post",
        contentType: "application/json",
        headers: {
            "X-CSRFToken": getCookie("csrf_token")
        },
        data: JSON.stringify(params),
        success: function (resp) {
            if (resp.errno == "0") {
                // 取消关注成功
                var count = parseInt($(".follows b").html());
                count--;
                $(".follows b").html(count + "")
                $(".focus").show()
                $(".focused").hide()
            }else if (resp.errno == "4101"){
                // 未登录，弹出登录框
                $('.login_form_con').show();
            }else {
                // 取消关注失败
                alert(resp.errmsg)
            }
        }
    })
});

//更新评论总数量
function updateCommentCount() {
    var count = $(".comment_list").length;
    $(".comment_count").html(count + "条评论")
}}