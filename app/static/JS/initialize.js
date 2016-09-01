$(function () {
    $('#container').highcharts({
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false
        },
        credits:{
            enabled:false // 禁用版权信息
        },
        title: {
            text: '各学院学生参加过竞赛比例'
        },
        subtitle: {
            text: '————教务处统计',
            align:'right',
        },
        //数据提示框
        tooltip: {
    	    pointFormat: '{series.name}: <b>{point.percentage:.1f}%</b>'
        },
        //标示线
        plotOptions: {
            pie: {
                allowPointSelect: true, //使数据可以选择
                dashStyle:'longdashdot', //标示线的样式，默认是solid（实线），这里定义为长虚线
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    color: '#000000',
                    connectorColor: '#000000',
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %'
                }
            }
        },
        //数据列
        series: [{
            type: 'pie',
            name: '比例',
            data: [
                ['软件工程学院',45.0],
                ['通信工程学院',26.8],
                {
                    name: '大气学院',
                    y: 12.8,
                    sliced: true,
                    selected: true
                },
                ['应用数学',    8.5],
                ['物理',     6.9],
            ]
        }]
        
    });
});	