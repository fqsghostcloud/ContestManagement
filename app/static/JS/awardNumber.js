$(function () {
    $('#container2').highcharts({
        chart: {
            type: 'column'
        },
        credits:{
            enabled:false, // 禁用版权信息
        },
        title: {
            text: '各学院获奖人数（分档次）',
        },
        subtitle: {
            text: '————教务处统计',
            align:'right',
        },
        xAxis: {
            categories: [
                '软件工程学院',
                '大气学院',
                '通信工程学院',

            ]
        },
        yAxis: {
            min: 0,
            title: {
                text: '获奖人数 (人)'
            }
        },
        tooltip: {
            headerFormat: '<span style="font-size:10px">{point.key}</span><table>',
            pointFormat: '<tr><td style="color:{series.color};padding:0">{series.name}: </td>' +
                '<td style="padding:0"><b>{point.y} 人</b></td></tr>',
            footerFormat: '</table>',
            shared: true,
            useHTML: true       //开启 HTML 模式后，就可以给提示框添加 链接、图片、表格等 HTML 元素
        },
        plotOptions: {
            column: {
                pointPadding: 0.2,
                borderWidth: 0,
                dataLabels:{
                    enabled:true,
                    style:{
                        color:'black',
                    },
                },
            },
        },
        series: [{
            name: '一档奖项',
            data: [5, 6, 4,]

        }, {
            name: '二档奖项',
            data: [12, 9, 16,]

        }, {
            name: '三档奖项',
            data: [20, 33, 39, ]

        }]
    });

});				