#!/usr/local/bin/perl
#
# Mijares Consultoría y Sistemas SL
# Derechos Reservados
# 2011 - 2012
# 

use strict;
use warnings;
use CGI;
use CGI::FormBuilder;
use Digest::MD5;
use PDF::Create;
use GD::Barcode::Code93;
use File::Temp;
use DBI;
use DateTime;
# use Data::Dumper;
$CGI::POST_MAX = 1024 * 10;  # max 10K posts
$CGI::DISABLE_UPLOADS = 1;  # no uploads 

my $html = CGI->new;
my $md5 = Digest::MD5->new;
# my $dsn = "DBI:mysql:database=rcv;";
my $dsn = "DBI:Pg:dbname=prueba2";

# Formulario para poliza nueva
my @campos = qw/fname lname doc ci tlf placa serial marca 
modelo year color clase tipo uso puestos user pass/;

my $lclase = [qw/CAMIONETA RUSTICO CAMION MOTOCICLETA
MINIBUS AUTOBUS REMOLQUE SEMIREMOLQUE AUTOMOVIL/];

my $luso = [qw/PARTICULAR TRANSP.PUBLICO TAXI CARGA SERV.URBANO
TRANSP.GANADO-EN-PIE/];

my $ltipo = [qw/PASEO PICK-UP PICKUP.BARANDA COUPE SEDAN TECHO.DURO 
CISTERNA FURGÓN CAMION ESTACA CAMIONETA VOLTEO CAVA JAULA RANCHERA VANS
TECHO.LONA SCOOTER CHUTO MINIBUS CHASIS TRANSP.PUBLICO PANEL COLECTIVO
BARANDA.HIERRO PLATAFORMA GRUA MOTOCICLETA SPORT.WAGON S-N CABINA 
PLATAFORMA.BARANDA CLUB.WAGON RACING BATEA SEMI.REMOLQUE BARANDA CASA.RODANTE/];

my %checks = (
    fname => 'FNAME',
    lname => 'LNAME',
    ci => '/^\d{7,9}$/',
    tlf => '/^0[24]\d{9}$/',
    placa => 'VALUE',
    serial => 'WORD',
    marca => 'VALUE',
    modelo => 'VALUE',
    year => '/^\d{4}$/',
    color => 'VALUE',
    puestos => 'INT'
    );

my %labels = (
    fname => 'Primer Nombre',
    lname => 'Primer Apellido',
    doc => 'Tipo Documento',
    ci => 'CI/RIF',
    tlf => 'Teléfono',
    placa => 'Placa',
    serial => 'Serial',
    marca => 'Marca',
    modelo => 'Modelo',
    year => 'Año',
    color => 'Color',
    clase => 'Clase',
    tipo => 'Tipo',
    uso => 'Uso',
    puestos => 'Nro. Puestos',
    user => 'Usuario',
    pass => 'Contraseña'
    );

my $form = CGI::FormBuilder->new(
    name => 'newrcv',
    title => 'Creación de Pólizas RCV',
    text => 'Complete la información cuidadosamente',
    method => 'post',
    stylesheet => '../css/estilo.css',
    fields => \@campos,
    validate => \%checks,
    fieldsets => [
	[comprador => 'Datos del Comprador'],
	[vehiculo => 'Datos del Vehículo'],
	[asesor => 'Datos del Asesor']
    ],
    keepextras => 1,
    labels => \%labels,
    messages => 'auto',
    required => 'ALL',
    reset => 'Limpiar Datos',
    submit => 'Generar RCV',
    );

$form->field(
    name => 'fname',
    fieldset => 'comprador'
    );

$form->field(
    name => 'lname',
    fieldset => 'comprador'
    );

$form->field(
    name => 'doc',
    fieldset => 'comprador',
    type => 'radio',
    options => [qw/V E J G P/]
    );

$form->field(
    name => 'ci',
    comment => 'Ej: 13229885',
    fieldset => 'comprador'
    );

$form->field(
    name => 'tlf',
    comment => 'Ej: 04145003856',
    fieldset => 'comprador'
    );

$form->field(
    name => 'placa',
    comment => 'Ej: CH540BA ó MFK33X',
    fieldset => 'vehiculo'
    );

$form->field(
    name => 'serial',
    comment => 'Serial de la Carrocería',
    fieldset => 'vehiculo'
    );

$form->field(
    name => 'marca',
    comment => 'Ej: FORD',
    fieldset => 'vehiculo'
    );

$form->field(
    name => 'modelo',
    comment => 'Ej: FIESTA',
    fieldset => 'vehiculo'
    );

$form->field(
    name => 'year',
    comment => 'Ej: 2012',
    fieldset => 'vehiculo'
    );

$form->field(
    name => 'color',
    comment => 'Ej: NEGRO',
    fieldset => 'vehiculo'
    );

$form->field(
    name => 'tipo',
    comment => 'Seleccione de la lista',
    fieldset => 'vehiculo',
    options => $ltipo,
    sortopts => 'NAME'
    );

$form->field(
    name => 'uso',
    comment => 'Seleccione de la lista',
    fieldset => 'vehiculo',
    options => $luso,
    sortopts => 'NAME'
    );

$form->field(
    name => 'clase',
    comment => 'Seleccione de la lista',
    options => $lclase,
    fieldset => 'vehiculo',
    sortopts => 'NAME'
    );

$form->field(
    name => 'puestos',
    comment => 'Ej: 5',
    fieldset => 'vehiculo',
    );

$form->field(
    name => 'user',
    fieldset => 'asesor'
    );

$form->field(
    name => 'pass',
    type => 'password',
    fieldset => 'asesor'
    );
####### Fin del Formulario ########

if ($form->submitted && $form->validate) {
    my $val = $form->fields;

        my $dbh = DBI->connect($dsn, 'pgsql') or
	print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=1')
	and exit 0;

    my $q1 = $dbh->prepare("SELECT id,pass,addr FROM asesor WHERE login = ?");
    my $q2 = $dbh->prepare("INSERT INTO vehiculo(placa, serial, marca, modelo,
year, color, clase, tipo, uso, puestos) VALUES(?,?,?,?,?,?,?,?,?,?)");
    my $q3 = $dbh->prepare("INSERT INTO poliza(fname, lname, doc, ci,
 tlf, asesor_id, vehiculo_id, hash, prima) VALUES(?,?,?,?,?,?,?,?,?)");

## Validamos usuario y password
    $q1->execute($val->{user});

    print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=2')
	and exit 0 unless ($q1->rows > 0);

    my @q1data = $q1->fetchrow_array;

    print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=3') 
	unless $q1data[1] eq $val->{pass};


## Generamos el HASH del documento
    $md5->add(uc ($val->{fname}), uc ($val->{lname}), $val->{doc},
	      $val->{ci}, $val->{tlf}, uc ($val->{placa}), uc ($val->{serial}),
	      uc ($val->{marca}), uc ($val->{modelo}), $val->{year},
	      uc ($val->{color}), $val->{clase}, $val->{tipo}, 
	      $val->{uso}, $val->{puestos}, $val->{user}); 

    my $digest = substr($md5->hexdigest,-16);
	  
## Calculamos coberturas, tasas y pagos

    my $cdc = 'Bs. 3.000'; my $tdc = '3,39%'; my $pdc = 'Bs. 101,80';
    my $cdp = 'Bs. 3.000'; my $tdp = '0,5%'; my $pdp = 'Bs. 15,00';
    my $cal = 'Bs. 3.000'; my $tal = '0,2%'; my $pal = 'Bs. 6,00';
    my $cma = 'Bs. 3.000'; my $tma = '1,02%'; my $pma = 'Bs. 30,50';
    my $cip = 'Bs. 2.000'; my $tip = '0,25%'; my $pip = 'Bs. 5,00';
    my $cgm = 'Bs. 500'; my $tgm = '0,32%'; my $pgm = 'Bs. 1,60';
    my $cis = 'Bs. 100'; my $tis = '0,12%'; my $pis = 'Bs. 0,10';
    my $tc = 'Bs. 14.600'; my $tp = 200,00;

    if ($val->{clase} eq 'MOTOCICLETA') {
	$cdc = 'Bs. 3.000'; $tdc = '3,20%'; $pdc = 'Bs. 95,90';
	$cdp = 'Bs. 3.000'; $tdp = '0,47%'; $pdp = 'Bs. 14,10';
	$cal = 'Bs. 0'; $tal = '%'; $pal = 'Bs. 0';
	$cma = 'Bs. 0'; $tma = '%'; $pma = 'Bs. 0';
	$cip = 'Bs. 0'; $tip = '%'; $pip = 'Bs. 0';
	$cgm = 'Bs. 0'; $tgm = '%'; $pgm = 'Bs. 0';
	$cis = 'Bs. 0'; $tis = '%'; $pis = 'Bs. 0';
	$tc = 'Bs. 6.000'; $tp = 150,00;
    }


if (($val->{tipo} eq 'PICK-UP') or
    ($val->{uso} eq 'TAXI') or
    ($val->{uso} eq 'TRANSP.PUBLICO' and $val->{puestos} <= 7)) {
	$tdc = '4,45%'; $pdc = 'Bs. 133,60';
	$tdp = '0,66%'; $pdp = 'Bs. 19,70';
	$tal = '0,26%'; $pal = 'Bs. 7,90';
	$tma = '1,33%'; $pma = 'Bs. 40,00';
	$tip = '0,33%'; $pip = 'Bs. 6,60';
	$tgm = '0,42%'; $pgm = 'Bs. 2,10';
	$tis = '0,16%'; $pis = 'Bs. 0,20';
	$tp = 250,00;
    }

if ($val->{uso} eq 'TRANSP.PUBLICO' and $val->{puestos} > 7) {
	$tdc = '7,42%'; $pdc = 'Bs. 222,70';
	$tdp = '1,09%'; $pdp = 'Bs. 32,80';
	$tal = '0,44%'; $pal = 'Bs. 13,10';
	$tma = '2,22%'; $pma = 'Bs. 66,70';
	$tip = '0,55%'; $pip = 'Bs. 10,90';
	$tgm = '0,70%'; $pgm = 'Bs. 3,50';
	$tis = '0,26%'; $pis = 'Bs. 0,30';
	$tp = 390,00;
    }

if ($val->{clase} eq 'CAMION') {
	$tdc = '5,30%'; $pdc = 'Bs. 159,00';
	$tdp = '0,78%'; $pdp = 'Bs. 23,40';
	$tal = '0,31%'; $pal = 'Bs. 9,40';
	$tma = '1,59%'; $pma = 'Bs. 47,60';
	$tip = '0,39%'; $pip = 'Bs. 7,80';
	$tgm = '0,50%'; $pgm = 'Bs. 2,50';
	$tis = '0,19%'; $pis = 'Bs. 0,20';
	$tp = 290,00;
    }
    
## Guardamos los valores en DB y manejamos errores
    
    unless (
	$q2->execute(
	    uc($val->{placa}),
	    uc($val->{serial}),
	    uc($val->{marca}),
	    uc($val->{modelo}),
	    $val->{year}, uc($val->{color}),
	    $val->{clase}, $val->{tipo}, $val->{uso},
	    $val->{puestos})
	) 


## Manejo de placas y seriales duplicados
    {
	if ($q2->errstr =~ /duplicate key .*vehiculo_placa_key/) {
	    print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=4');
	    print STDERR $q2->err;
	    exit 0;
	}
	
	elsif ($q2->errstr =~ /duplicate key .*vehiculo_serial_key/) {
	    print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=5');
	    print STDERR $q2->err;
	    exit 0;
	}

	else {
	    print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=6');
	    print STDERR $q2->err;
	    exit 0;
	}		
    }

    my $car = $dbh->last_insert_id(undef, undef, 'vehiculo', undef);

    unless (
	$q3->execute(
	    uc($val->{fname}),
	    uc($val->{lname}),
	    $val->{doc}, $val->{ci},
	    $val->{tlf}, 
	    $q1data[0], # asesor_id
	    $car, # vehiculo_id
	    $digest,
	    $tp)
	) 

## Manejo de problemas con polizas
    {
	# if ($q3->errstr =~ /duplicate key .*vehiculo_placa_key/) {
	#     print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=4');
	#     print STDERR $q3->err;
	#     exit 0;
	# }
	
	# elsif ($q3->errstr =~ /duplicate key .*vehiculo_serial_key/) {
	#     print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=5');
	#     print STDERR $q3->err;
	#     exit 0;
	# }

	# else {
	    print $html->redirect('http://www.pyugmao.com.ve/cgi/error.cgi?err=7');
	    print STDERR $q3->err;
	    exit 0;
#	}		
    }


	
# Obtengo el ID para Nro Contrato y desconecto.

    my $contrato = $dbh->last_insert_id(undef, undef, 'poliza', undef);

    $q1->finish;
    $q2->finish;
    $q3->finish;
    $dbh->disconnect;

## Se crea la imagen barcode en un archivo temp

    my $fh = File::Temp->new(SUFFIX => '.jpg');

    binmode $fh;

    my $bars = $fh->filename;

    print $fh GD::Barcode::Code93->new($digest)->plot(Height => 38)->jpeg;

    close $fh;

## Creamos el PDF y se envia al browser

    print $html->header(-type => 'application/x-pdf',
			-attachment => 'rcv.pdf',
			-charset => 'UTF-8');

    my $pdf = PDF::Create->new(
	'filename' => '-',
	'Author' => 'Inversiones Pyugmao 2009, C.A.',
	'Title' => 'Poliza RCV',
	'CreationDate' => [localtime]
	);

    my $jpg = $pdf->image($bars);

    my $root = $pdf->new_page('MediaBox' => [0, 0, 612, 396]);
    my $rcv = $root->new_page;
    my $font1 = $pdf->font('BaseFont' => 'Courier-Bold');
    my $font2 = $pdf ->font('BaseFont' => 'Courier');
    
    my $start = DateTime->now(time_zone => 'America/Caracas');
    my $end = $start->clone->add(years => 1);

    # nro contrato
    $rcv->string($font1, 8, &xp(80), &yp(113), sprintf("%08d",$contrato));

    # fecha de inicio
    $rcv->string($font1, 8, &xp(120), &yp(113), $start->dmy('/'));

    # fecha vencimiento
    $rcv->string($font1, 8, &xp(171), &yp(113), $end->dmy('/'));

    # nombre y apellido
    $rcv->string($font1, 8, &xp(40), &yp(92), uc($val->{fname}) . 
						  ' ' . uc($val->{lname}));

    # tipo y numero documento
    $rcv->string($font1, 8, &xp(130), &yp(92), $val->{doc} . '-' . $val->{ci});

    # tlf
    $rcv->string($font1, 8, &xp(172), &yp(92), $val->{tlf});

    # direccion
    $rcv->string($font1, 8, &xp(40), &yp(84), $q1data[2]);

    # Asesor
    $rcv->string($font2, 8, &xp(127), &yp(84), 'Angel Figuera (0416-826.94.44)');

    # datos del vehiculo
    $rcv->string($font2, 8, &xp(43), &yp(77), 'DATOS DEL VEHICULO');
    $rcv->string($font2, 8, &xp(20), &yp(74), 'PLACA:');
    $rcv->string($font1, 8, &xp(20), &yp(71), uc($val->{placa}));
    $rcv->string($font2, 8, &xp(36), &yp(74), 'MARCA:');
    $rcv->string($font1, 8, &xp(36), &yp(71), uc($val->{marca}));
    $rcv->string($font2, 8, &xp(59), &yp(74), 'MODELO:');
    $rcv->string($font1, 8, &xp(59), &yp(71), uc($val->{modelo}));
    $rcv->string($font2, 8, &xp(83), &yp(74), 'COLOR:');
    $rcv->string($font1, 8, &xp(83), &yp(71), uc($val->{color}));
    $rcv->string($font2, 8, &xp(20), &yp(67), 'ANO:');
    $rcv->string($font1, 8, &xp(20), &yp(64), $val->{year});
    $rcv->string($font2, 8, &xp(35), &yp(67), 'SERIAL:');
    $rcv->string($font1, 8, &xp(35), &yp(64), uc($val->{serial}));
    $rcv->string($font2, 8, &xp(75), &yp(67), 'CLASE:');
    $rcv->string($font1, 8, &xp(75), &yp(64), $val->{clase});
    $rcv->string($font2, 8, &xp(20), &yp(60), 'USO:');
    $rcv->string($font1, 8, &xp(20), &yp(57), $val->{uso});
    $rcv->string($font2, 8, &xp(55), &yp(60), 'PUESTOS:');
    $rcv->string($font1, 8, &xp(55), &yp(57), $val->{puestos});
    $rcv->string($font2, 8, &xp(75), &yp(60), 'TIPO:');
    $rcv->string($font1, 8, &xp(75), &yp(57), $val->{tipo});

    # coberturas

    $rcv->string($font1, 7, &xp(119), &yp(78), 'DESCRIPCION');
    $rcv->string($font2, 7, &xp(119), &yp(75), 'DANOS A COSAS');
    $rcv->string($font2, 7, &xp(119), &yp(72), 'DANOS A TERCEROS');
    $rcv->string($font2, 7, &xp(119), &yp(69), 'ASISTENCIA LEGAL');
    $rcv->string($font2, 7, &xp(119), &yp(66), 'MUERTE ACCIDENTE TRANS.');
    $rcv->string($font2, 7, &xp(119), &yp(63), 'INVAL. PARCIAL Y PERM.');
    $rcv->string($font2, 7, &xp(119), &yp(60), 'GASTOS MEDICOS');
    $rcv->string($font2, 7, &xp(119), &yp(57), 'INDEMNIZACION SEMANAL');
    $rcv->string($font2, 7, &xp(119), &yp(54), 'GASTOS DE EMISION');
    $rcv->string($font1, 7, &xp(119), &yp(51), 'TOTAL COBERTURAS');
    $rcv->line(&xp(118), &yp(50), &xp(206), &yp(50));
    $rcv->string($font1, 7, &xp(119), &yp(48), 'TOTAL PAGO');
    $rcv->string($font1, 7, &xp(158), &yp(78), 'COBERTURA');
    $rcv->string($font2, 7, &xp(158), &yp(75), $cdc);
    $rcv->string($font2, 7, &xp(158), &yp(72), $cdp);
    $rcv->string($font2, 7, &xp(158), &yp(69), $cal);
    $rcv->string($font2, 7, &xp(158), &yp(66), $cma);
    $rcv->string($font2, 7, &xp(158), &yp(63), $cip);
    $rcv->string($font2, 7, &xp(158), &yp(60), $cgm);
    $rcv->string($font2, 7, &xp(158), &yp(57), $cis);
    $rcv->string($font1, 7, &xp(158), &yp(51), $tc);
    $rcv->string($font1, 7, &xp(177), &yp(78), 'TASA');
    $rcv->string($font2, 7, &xp(177), &yp(75), $tdc);
    $rcv->string($font2, 7, &xp(177), &yp(72), $tdp);
    $rcv->string($font2, 7, &xp(177), &yp(69), $tal);
    $rcv->string($font2, 7, &xp(177), &yp(66), $tma);
    $rcv->string($font2, 7, &xp(177), &yp(63), $tip);
    $rcv->string($font2, 7, &xp(177), &yp(60), $tgm);
    $rcv->string($font2, 7, &xp(177), &yp(57), $tis);
    $rcv->string($font1, 7, &xp(191), &yp(78), 'PAGO');
    $rcv->string($font2, 7, &xp(191), &yp(75), $pdc);
    $rcv->string($font2, 7, &xp(191), &yp(72), $pdp);
    $rcv->string($font2, 7, &xp(191), &yp(69), $pal);
    $rcv->string($font2, 7, &xp(191), &yp(66), $pma);
    $rcv->string($font2, 7, &xp(191), &yp(63), $pip);
    $rcv->string($font2, 7, &xp(191), &yp(60), $pgm);
    $rcv->string($font2, 7, &xp(191), &yp(57), $pis);
    $rcv->string($font2, 7, &xp(191), &yp(54), 'Bs. 40,00');
    $rcv->string($font1, 7, &xp(191), &yp(48), "Bs. $tp");


    # Carnet desprendible (2)

    $rcv->string($font1, 6, &xp(88), &yp(28), 'Nro: ' . sprintf("%08d",$contrato));
    $rcv->string($font1, 6, &xp(124), &yp(28), 'VENCE: ' . $end->dmy('/'));
    $rcv->string($font1, 6, &xp(88), &yp(24), 'TOMADOR: ' . uc($val->{fname}) .
		 ' ' . uc($val->{lname}) . '    ' . $val->{doc} . '-' . $val->{ci});
    $rcv->string($font1, 6, &xp(88), &yp(20), 'PLACA: ' . uc($val->{placa}));
    $rcv->string($font1, 6, &xp(115), &yp(20), 'S.N: ' . uc($val->{serial}));
    $rcv->string($font1, 6, &xp(88), &yp(16), 'MARCA: ' . uc($val->{marca}));
    $rcv->string($font1, 6, &xp(105), &yp(16), 
		 'MODELO: ' . sprintf("%-10s",uc($val->{modelo})) . 
	'  ANO: ' . $val->{year});
    $rcv->string($font1, 6, &xp(88), &yp(12), 
		 'COLOR: ' . sprintf("%-8s",uc($val->{color})) .
		 ' CLASE: ' . sprintf("%-8s",$val->{clase}) .
		 ' TIPO: ' . sprintf("%-8s",$val->{tipo}));
    $rcv->string($font1, 6, &xp(88), &yp(8),
		 'USO: ' . $val->{uso} .
		 '      PUESTOS: ' . $val->{puestos});
    $rcv->string($font1, 6, &xp(98), &yp(4), 
		 'TOTAL COBERTURA: ' . $tc);


    $rcv->string($font1, 6, &xp(150), &yp(28), 'Nro: ' . sprintf("%08d",$contrato));
    $rcv->string($font1, 6, &xp(184), &yp(28), 'VENCE: ' . $end->dmy('/'));
    $rcv->string($font1, 6, &xp(150), &yp(24), 'TOMADOR: ' . uc($val->{fname}) .
		 ' ' . uc($val->{lname}) . '    ' . $val->{doc} . '-' . $val->{ci});
    $rcv->string($font1, 6, &xp(150), &yp(20), 'PLACA: ' . uc($val->{placa}));
    $rcv->string($font1, 6, &xp(177), &yp(20), 'S.N: ' . uc($val->{serial}));
    $rcv->string($font1, 6, &xp(150), &yp(16), 'MARCA: ' . uc($val->{marca}));
    $rcv->string($font1, 6, &xp(167), &yp(16), 
		 'MODELO: ' . sprintf("%-10s",uc($val->{modelo})) . 
	'  ANO: ' . $val->{year});
    $rcv->string($font1, 6, &xp(150), &yp(12), 
		 'COLOR: ' . sprintf("%-8s",uc($val->{color})) .
		 ' CLASE: ' . sprintf("%-8s",$val->{clase}) .
		 ' TIPO: ' . sprintf("%-8s",$val->{tipo}));
    $rcv->string($font1, 6, &xp(150), &yp(8),
		 'USO: ' . $val->{uso} .
		 '      PUESTOS: ' . $val->{puestos});
    $rcv->string($font1, 6, &xp(160), &yp(4), 
		 'TOTAL COBERTURA: ' . $tc);
		 

    $rcv->image('image' => $jpg, 
		'xpos' => &xp(12), 
		'ypos' => &yp(22));
    
    $pdf->close;
    

} else {
    
# Creamos el HTML para crear una nueva poliza RCV    

print $html->header(
    -charset => 'utf-8'
    );

print $html->start_html(
    -title => 'Formulario de Solicitud de Documentos',
    -style => {'src' => '/css/estilo.css'},
    -encoding => 'utf-8',
    -lang => 'es_VE'
    ),
    
    $html->div(
	{-class => 'logo'}, 
	$html->div({-class => 'titulo'},'')
    ),
	$html->div(
	    {-class => 'menu'},
	    $html->a({-href => '../index.html'}, 'Home'),
	    $html->a({-href => '../servicios.html'}, 'Servicios'),
	    $html->a({-href => '../rs.html'}, 'Responsabilidad Civíl'),
	    $html->a({-href => '../tarifas.html'}, 'Tarifas'),
	    $html->a({-href => '../contacto.html'}, 'Contacto')
	),
	    $html->div({-class => 'cuerpo'},
		       
		       $html->h1('Complete el Formulario'),
		       $form->render
	    );
print $html->end_html;
}


## funciones para pasar de milimetros a puntos (la medida de la hoja) ##
    sub xp {
	my $x = shift;
	$x *= 2.87323943662;
	return int($x);
    }
    
    sub yp {
	my $y = shift;
	$y *= 2.78873239473;
	return int($y);
    }
    
