$(document).on('ready', function () {
    $(".vertical").slick({
      dots: true,
      infinite: true,
      centerMode: true,
      arrows : true,
      autoplay : true,
      autoplaySpeed : 3000,
      pauseOnHover : true,
      slidesToShow: 1,
      slidesToScroll: 1,
      responsive: [ // 반응형 웹 구현 옵션
					{  
						breakpoint: 1250, //화면 사이즈 960px
						settings: {
							//위에 옵션이 디폴트 , 여기에 추가하면 그걸로 변경
							arrows : false,
						} 
					},
				]
    });
  });