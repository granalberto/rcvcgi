#!/usr/bin/perl

use warnings;
use strict;
use CGI;


my $html = CGI->new;

my $mensaje;

sub cuerpo {

    my $error = shift;

    if ($error == 1) {
	$mensaje = 'Base de Datos NO Disponible';
    }

    elsif ($error == 2) {
	$mensaje = 'Usuario Incorrecto';
    }

    elsif ($error == 3) {
	$mensaje = 'Clave Incorrecta';
    }

    elsif ($error == 4) {
	$mensaje = 'Placa registrada en la Base de Datos';
    }
    
    elsif ($error == 5) {
	$mensaje = 'Serial registrado en la Base de Datos';
    }
    
    elsif ($error == 6) {
	$mensaje = 'No se pudo ingresar el Registo en Base de Datos';
    }

    else { $mensaje = 'No intentes cosas extrañas'; }

    print $html->header;
    
    print $html->start_html(
	-title => 'Formulario de Solicitud de Documentos',
	-style => {'src' => '../css/estilo.css'},
	-encoding => 'utf-8',
	-lang => 'es-VE'
	),
	
	$html->div(
	    {-class => 'logo'}, 
	    $html->div({-class => 'titulo'},'')
	),
	    $html->div(
		{-class => 'menu'},
		$html->a({-href => '../index.html'}, 'Home'),
		$html->a({-href => '../servicios.html'}, 'Servicios'),
		$html->a({-href => '../rs.html'}, 'Responsabilidad Social'),
		$html->a({-href => '../tarifas.html'}, 'Tarifas'),
		$html->a({-href => '../contacto.html'}, 'Contacto')
	    ),
		$html->div({-class => 'cuerpo'}, 
			   $html->h1($mensaje)
		);
    print $html->end_html;
}



#Generamos el HTML

print $html->redirect('http://www.pyugmao.com.ve') unless ($html->param);

&cuerpo($html->param('err'));
