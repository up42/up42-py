<?xml version="1.0"?>

<!-- 
Description : Stylesheet for Pleiades products
Version : 5.0.1
DIT 26407: Evolution du DIMAP V2 avec les nouvelles nomenclatures Astrium Services / SPOT IMAGE dans les labels et les Copyright
DIT 32740: DIMAP Format Rebranding (nouvelle marque AIRBUS)
-->

<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
	<xsl:template match="/">
		<html>
	
			<head>
				<meta http-equiv="content-type" content="text/html;charset=ISO-8859-1"/>
				<title>dimap</title>
				<style type="text/css">
					<!--.entete { color: #fff; font-style: italic; font-weight: bolder; font-size: 14px; font-family: Georgia, "Times New Roman" }-->
					.entete { color: #333366; font-weight: bolder; font-size: 14px; font-family: Verdana, Arial }
					<!--.titre  { font-weight: bolder; font-size: 20px; font-family: Georgia, "Times New Roman"; text-align: center }-->
					.titre  { font-weight: bolder; font-size: 20px; font-family: Verdana, Arial ; text-align: center }
					<!--.spotview { color: white; font-weight: bolder; font-size: 32px; font-family: Verdana, "Times New Roman"; text-align: center }-->
					.spotview { color: white; font-weight: bolder; font-size: 32px; font-family: Verdana, Arial ; text-align: center }
					<!--.intitule { font-weight: bolder; font-size: 11px; font-family: Verdana, Arial }-->
					.intitule { font-weight: bolder; font-size: 11px; font-family: Verdana, Arial }
					<!--.intitule2 { color: silver; font-weight: bolder; font-size: 11px; font-family: Verdana, Arial }-->
					.intitule2 { color: #333366; font-weight: bolder; font-size: 11px; font-family: Verdana, Arial; text-decoration: underline }
					.description { font-size: 11px; font-family: Verdana, Arial }
					.affiche { display : show }
					.masque { display  : none }
			
					<!--.onglets   {  font-weight: bolder; font-size: 11px; font-family: Verdana, Helvetica; text-decoration: none; text-align: center }
					.ongletsOn {  font-weight: bolder; font-size: 11px; font-family: Verdana, Helvetica; text-decoration: none; text-align: center }-->
					.onglets   {  font-weight: bolder; font-size: 11px; font-family: Verdana, Arial; text-decoration: none; text-align: center }
					.ongletsOn {  font-weight: bolder; font-size: 11px; font-family: Verdana, Arial; text-decoration: none; text-align: center }
			
					<!--a.onglets    { color: #00607a; text-decoration: none; }
					a.onglets:active  { color: #00607a }
					a.onglets:hover  { color: white; text-decoration: none }-->
					a.onglets    { color: #333366; text-decoration: none; }
					a.onglets:active  { color: white }
					a.onglets:hover  { color: #333366; text-decoration: none }
			
					<!--a.ongletsOn    { color: #000000; text-decoration: none }
					a.ongletsOn:active  { color: #000000 }
					a.ongletsOn:hover  { color: #000000; text-decoration: none }-->
					a.ongletsOn    { color: white; text-decoration: none }
					a.ongletsOn:active  { color: white }
					a.ongletsOn:hover  { color: white; text-decoration: none }
			
					<!--div.onglets {background-color : #bbbbbb; }
					div.ongletsOn {background-color : #e4decb; }-->
					div.onglets { }
					div.ongletsOn {background-color : #FF5601; }
			
					<!--td.onglets {background-color : #bbbbbb; border-style : solid; border-width : 1pt; border-color : black;}
					td.ongletsOn {background-color : #e4decb;  border-style : solid; border-width : 1pt; border-color : black;}-->
					td.onglets { }
					td.ongletsOn {background-color : #FF5601; }
			
					.ROI { border-style : thin-solid; border-color : white;}
					.ROIshow {  border-left : white 1px solid ; border-right : white 1px solid; border-bottom : white 1px solid ; border-top : white 1px solid ; display : show; visibility : visible }
				</style>
			
				<script language="javascript">
					var strPreviousOn = "description" ;
			
					function releaseFunc(strFunc) {
						var str = "divO_" + strFunc;
						var divelt = document.getElementById(str);
						divelt.className="onglets";
						
						str = "tdO_" + strFunc;
						divelt = document.getElementById(str);
						divelt.className="onglets";
						
						str = "aO_" + strFunc;
						divelt = document.getElementById(str);
						divelt.className="onglets";
					}
			
					function selectFunc(strFunc) {
						var str = "divO_" + strFunc;
						var divelt = document.getElementById(str);
						divelt.className="ongletsOn";
						
						str = "tdO_" + strFunc;
						divelt = document.getElementById(str);
						divelt.className="ongletsOn";
						
						str = "aO_" + strFunc;
						divelt = document.getElementById(str);
						divelt.className="ongletsOn";
			
						strPreviousOn = strFunc;
					}
				
					function details(strId) {
						var divelt = document.getElementById(strId);
						if (divelt.className=="masque") {
							divelt.className="affiche";
						}
						else {
							divelt.className="masque";
						}
					}
			
					function expandSources() {
						<xsl:for-each select="//Source_Information">
							eval('div<xsl:value-of select="position()"/>.className = \'affiche\'');
						</xsl:for-each>
					}
			
					function onWindowResize(e) {
			//			if (document.readyState == "loaded") {
							organize(strPreviousOn);
			//			}
					}
						
					// Taille de la scene
					function calcSceneSize() {
						frame_w = 0;
						frame_h = 0;
						<xsl:for-each select="//Dataset_Content/Dataset_Extent/Vertex">
							frame_w = Math.max(frame_w, <xsl:value-of select="COL"/>);
							frame_h = Math.max(frame_h, <xsl:value-of select="ROW"/>);
						</xsl:for-each> 
					}
			
				
					function organize(strMode) {
					
						switch(strMode) {
							case "description":
								document.getElementById("divGenInfo").className  = "affiche";
								document.getElementById("divImgDim").className = "affiche";
								document.getElementById("divDtstFrm").className = "affiche";
								document.getElementById("divSources").className = "masque";
								document.getElementById("divCRS").className = "masque";
								document.getElementById("divGEO").className = "masque";
								document.getElementById("divProd").className = "affiche";
								document.getElementById("divQuicklook").className  = "masque";
								break;
					
							case "quicklook":
								document.getElementById("divGenInfo").className  = "masque";
								document.getElementById("divImgDim").className = "masque";
								document.getElementById("divDtstFrm").className = "masque";
								document.getElementById("divSources").className = "masque";
								document.getElementById("divCRS").className = "masque";
								document.getElementById("divGEO").className = "masque";
								document.getElementById("divProd").className = "masque";
								document.getElementById("divQuicklook").className  = "affiche";
								updateROIs();
								break;
			
							case "lineage":
								document.getElementById("divGenInfo").className  = "masque";
								document.getElementById("divImgDim").className = "masque";
								document.getElementById("divDtstFrm").className = "masque";
								document.getElementById("divCRS").className = "masque";
								document.getElementById("divGEO").className = "masque";
								document.getElementById("divQuicklook").className  = "masque";
								document.getElementById("divProd").className = "affiche";
								document.getElementById("divSources").className = "affiche";
								break;
			
							case "crs":
								document.getElementById("divGenInfo").className  = "masque";
								document.getElementById("divImgDim").className = "masque";
								document.getElementById("divDtstFrm").className = "masque";
								document.getElementById("divSources").className = "masque";
								document.getElementById("divCRS").className = "affiche";
								document.getElementById("divGEO").className = "affiche";
								document.getElementById("divProd").className = "masque";
								document.getElementById("divQuicklook").className  = "masque";
								break;
			
							case "globalinfo":
								document.getElementById("divGenInfo").className  = "affiche";
								document.getElementById("divImgDim").className = "affiche";
								document.getElementById("divDtstFrm").className = "affiche";
								document.getElementById("divSources").className = "affiche";
								document.getElementById("divCRS").className = "affiche";
								document.getElementById("divGEO").className = "affiche";
								document.getElementById("divProd").className = "affiche";
								document.getElementById("divQuicklook").className  = "affiche";
								updateROIs();	
								break;
					
							default:
								return false;
								break;
						}
					
						releaseFunc(strPreviousOn);
						selectFunc(strMode);
						
						updateROIQc();
					}				
				
					function updateROIs() {
						x = 0;
						y = 0;
						obj = document.getElementById("imgQl");
						while (obj.offsetParent != null) {
							x += obj.offsetLeft;
							y += obj.offsetTop;
							obj = obj.offsetParent;
						}
						x += obj.offsetLeft;
						y += obj.offsetTop;
						
						// Taille de la scene d'origine
						calcSceneSize();
					}
					
					function updateROIQc() {	
						x = 0;
						y = 0;
						obj = document.getElementById("imgQc");
						
						while (obj.offsetParent != null) {
							x += obj.offsetLeft;
							y += obj.offsetTop;
							obj = obj.offsetParent;
						}
						x += obj.offsetLeft;
						y += obj.offsetTop;
				
						// Taille de la scene d'origine
						calcSceneSize();
						
						// Gestion de la marge autour de l'icone
						var imaQl = new Image();
						imaQl.src =  "preview.jpg";
						hQC = 128 * imaQl.height / 1000;
					}					
				</script>
			</head>
	
			<!--body bgcolor="#e4decb" onload="organize('description')" onresize="onWindowResize()"-->
			<!-- Changement du fond de couleur en blanc -->
			<body onload="organize('description')" onresize="onWindowResize()">
				<div align="center">
					<table border="0" cellpadding="0" cellspacing="0" id="tblOnglets" width="80%">
						<tr height="20">
							<td width="100" border="0" height="20" id="tdO_description">
								<div id="divO_description" class="ongletsOn">
									<a id="aO_description" class="ongletsOn" href="javascript:organize('description')">Description</a>
								</div>
							</td>
							<td width="10" border="0" height="20"></td>
							<td width="100" height="20" id="tdO_lineage" class="onglets">
								<div id="divO_lineage" class="onglets">
									<a id="aO_lineage" class="onglets" href="javascript:organize('lineage')">Lineage</a>
								</div>
							</td>
							<td width="10" height="20"></td>
							<td width="140" height="20" id="tdO_crs" class="onglets">
								<div id="divO_crs" class="onglets">
									<a id="aO_crs" class="onglets" href="javascript:organize('crs')">Coordinate System</a>
								</div>
							</td>
							<td width="10" height="20"></td>
							<td width="100" height="20" id="tdO_quicklook" class="onglets">
								<div id="divO_quicklook" class="onglets">
									<a id="aO_quicklook" class="onglets" href="javascript:organize('quicklook')">Quicklook</a>
								</div>
							</td>
							<td width="40" height="20"></td>
							<td width="150" height="20" id="tdO_globalinfo" class="onglets">
								<div id="divO_globalinfo" class="onglets">
									<a id="aO_globalinfo" class="onglets" href="javascript:organize('globalinfo')">Printable information</a>
								</div>
							</td>
							<td width="10" height="20"></td>
						</tr>
						<tr height="5"></tr>
					</table>
				</div>
				<div align="center">
					<table border="0" cellpadding="0" cellspacing="0" width="80%">
						<tr>
							<td>
								<table border="0" cellpadding="0" cellspacing="0" width="100%">
									<tr>
										<td>
											<table border="0" cellpadding="0" cellspacing="0" width="100%">
												<tr>
													<td width="120">
														<div align="center">
															<a target="_blank" title="quicklook">
																<xsl:attribute name="href">
																	<xsl:value-of select="//DATASET_QL_PATH/@href"/>
																</xsl:attribute>
																<img border="0" id="imgQc">
																	<xsl:attribute name="src">
																		<xsl:value-of select="//DATASET_TN_PATH/@href"/>
																	</xsl:attribute>
																</img>
															</a>
														</div>
													</td>
													<td width="63%"> <!-- ATTENTION: cette dimension conditionne la place du logo AIRBUS (non colle a droite) -->
														<table border="0" cellpadding="2" cellspacing="5">
															<xsl:if test="//GEOMETRIC_PROCESSING">
																<tr>
																	<td width="8"></td>
																	<!--td bgcolor="#00607a" width="70"-->
																	<td width="70">
																		<p class="intitule2"> TYPE:</p>
																		<!--hr color="#333366"/-->
																</td>
																	<td width="20"></td>
																	<td>
																		<p class="intitule">
																			<xsl:value-of select="//Processing_Information/Product_Settings/Geometric_Settings/GEOMETRIC_PROCESSING"/>
																		</p>
																	</td>
																</tr>
															</xsl:if>
															<xsl:if test="//DATASET_NAME">
																<tr>
																	<td width="8"></td>
																	<td width="70">
																		<p class="intitule2"> LAYER:</p>
																	</td>
																	<td width="20"></td>
																	<td>
																		<p class="intitule">
																			<xsl:value-of select="//Dataset_Identification/DATASET_NAME"/>
																		</p>
																	</td>
																</tr>
															</xsl:if>
															<xsl:if test="//METADATA_FORMAT">
																<tr>
																	<td width="8"></td>
																	<td width="70">
																		<p class="intitule2"> FORMAT:</p>
																	</td>
																	<td width="20"></td>
																	<td>
																		<p class="intitule">
																			<xsl:value-of select="//Metadata_Identification/METADATA_FORMAT"/>
																		</p>
																	</td>
																</tr>
															</xsl:if>
															<xsl:if test="//DATA_FILE_FORMAT">
																<tr>
																	<td width="8"></td>
																	<td width="70">
																		<p class="intitule2"> RASTER:</p>
																	</td>
																	<td width="20"></td>
																	<td>
																		<p class="intitule">
																			<xsl:value-of select="//Data_Access/DATA_FILE_FORMAT"/>
																		</p>
																	</td>
																</tr>
															</xsl:if>
														</table>
													</td>
													<td>
														<div align="left"> <!-- Logo aligne a gauche pour marge a droite -->
															<p>
																<img WIDTH="150" src="LIBRARY/LOGO.JPG" align="middle"/>
															</p>
														</div>
													</td>
												</tr>
											</table>
										</td>
									</tr>
								</table>
							</td>
						</tr>
					</table>
			
					<br/>
					<div id="divGenInfo" class="affiche">
						<table border="0" cellpadding="0" cellspacing="0" width="80%" >
							<tr>
								<td valign="middle" align="center">
									<br/>
									<table border="0" cellpadding="0" cellspacing="0" width="100%">
										<tr>
											<td valign="top">
												<table border="0" cellpadding="0" cellspacing="2" width="100%">
													<tr>
														<td>
															<p>
																<span class="entete">General Information</span>
																<hr color="#333366"/>
															</p>
														</td>
													</tr>
												</table>
												<br/>
												<table border="0" cellpadding="0" cellspacing="0" width="100%">
													<tr>
														<td valign="top">
															<p class="intitule">
																<b>Map Name</b>
															</p>
														</td>
														<td>
															<p class="description">
																<xsl:value-of select="//Dataset_Identification/DATASET_NAME"/>
																<br/>
																<br/>
															</p>
														</td>
													</tr>
													<xsl:if test="//GEOMETRIC_PROCESSING">
														<tr>
															<td valign="top">
																<p class="intitule">
																	<b>Geometric Processing Level</b>
																</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//Processing_Information/Product_Settings/Geometric_Settings/GEOMETRIC_PROCESSING"/>
																	<br/>
																	<br/>
																</p>
															</td>
														</tr>
													</xsl:if>
													<xsl:if test="//Processing_Information">
														<tr>
															<td valign="top">
																<p class="intitule">
																	<b>Radiometric Processing Level</b>
																</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//Processing_Information/Product_Settings/Radiometric_Settings/RADIOMETRIC_PROCESSING"/>
																	<br/>
																	<br/>
																</p>
															</td>
														</tr>
													</xsl:if>
												</table>
											</td>
										</tr>
									</table>
									<br/>
								</td>
							</tr>
						</table>
					</div>	<!-- /GenInfo -->
		
					<a name="description"></a>
					<div id="divImgDim" class="affiche">
						<br/>
						<xsl:if test="//Raster_Dimensions">
							<table border="0" cellpadding="0" cellspacing="0" width="80%" >
								<tr>
									<td valign="middle" align="center">
										<br/>
										<table border="0" cellpadding="0" cellspacing="0" width="100%">
											<tr>
												<td valign="top">
													<table border="0" cellpadding="0" cellspacing="2" width="100%">
														<tr>
															<td>
																<p>
																	<span class="entete">Image dimensions</span>
																	<hr color="#333366"/>
															</p>
															</td>
														</tr>
													</table>
													<br/>
													<table border="0" cellpadding="0" cellspacing="5" width="100%">
														<xsl:if test="//NCOLS">
															<tr>
																<td valign="top" width="300">
																	<p class="intitule">Number of columns</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//NCOLS"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<xsl:if test="//NROWS">
															<tr>
																<td valign="top" width="300">
																	<p class="intitule">Number of rows</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//NROWS"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<xsl:if test="//NBANDS">
															<tr>
																<td valign="top" width="300">
																	<p class="intitule">Number of spectral bands</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//NBANDS"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
													</table>
												</td>
											</tr>
										</table>
										<br/>
									</td>
								</tr>
							</table>
						</xsl:if>
					</div> <!-- /divImgDim -->
		
					<a name="sourceinfo"></a>
					<div id="divDtstFrm" class="affiche">
						<xsl:if test="//Dataset_Extent">
							<br/>
							<table border="0" cellpadding="0" cellspacing="0" width="80%" >
								<tr>
									<td valign="middle" align="center">
										<br/>
										<table border="0" cellpadding="0" cellspacing="0" width="100%">
											<tr>
												<td valign="top">
													<table border="0" cellpadding="0" cellspacing="2" width="100%">
														<tr>
															<td>
																<p>
																	<span class="entete">Dataset framing</span>
																	<hr color="#333366"/>
															</p>
															</td>
														</tr>
													</table>
													<br/>
													<table border="0" cellpadding="0" cellspacing="2" width="100%">
														<tr>
															<td valign="top" width="33%">
																<p class="intitule">Vertice</p>
															</td>
															<td valign="top" width="33%">
																<p class="description">
																	<span class="intitule">Longitude </span>(DEG)</p>
															</td>
															<td>
																<p class="description">
																	<span class="intitule">Latitude </span>(DEG)</p>
															</td>
															<td>
																<p class="description">
																	<span class="intitule">Row </span>
																</p>
															</td>
															<td>
																<p class="description">
																	<span class="intitule">Col </span>
																	<br/>
																</p>
															</td>
														</tr>
														<xsl:for-each select="//Dataset_Extent/Vertex">
															<tr>
																<td valign="top" width="33%">
																	<p class="description">#<xsl:value-of select="position()"/>
																	</p>
																</td>
																<td valign="top" width="33%">
																	<p class="description">
																		<xsl:value-of select="LON"/>
																	</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="LAT"/>
																	</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="ROW"/>
																	</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="COL"/>
																	</p>
																</td>
															</tr>
														</xsl:for-each>
													</table>
												</td>
											</tr>
										</table>
										<br/>
									</td>
								</tr>
							</table>
						</xsl:if>
					</div> <!-- /divDtstFrm -->
		
					<div id="divSources" class="masque">
						<br/>
						<table border="0" cellpadding="0" cellspacing="0" width="80%" >
							<tr>
								<td valign="middle" align="center">
									<br/>
									<table border="0" cellpadding="0" cellspacing="0" width="100%">
										<tr>
											<td valign="top">
												<table border="0" cellpadding="0" cellspacing="2" width="100%">
													<tr>
														<td>
															<p>
																<span class="entete">Dataset sources</span>
																<hr color="#333366"/>
															</p>
														</td>
													</tr>
												</table>
												<br/>
												<table border="0" cellpadding="0" cellspacing="5" width="100%">
										
													<xsl:for-each select="//Source_Identification">
														<tr>
															<td valign="top" width="50">
																<p class="intitule">
																	<a title="show / hide details">
																		<xsl:attribute name="href">javascript:details("div<xsl:value-of select="generate-id()"/>")</xsl:attribute>
																		<xsl:value-of select="Strip_Source/MISSION"/>
																	</a>
																</p>
															</td>
															<td class="description">
																<xsl:value-of select="SOURCE_ID"/>
															</td>
														</tr>
														<tr>
															<td valign="top"></td>
															<td>
																<div class="masque">
																	<xsl:attribute name="id">div<xsl:value-of select="generate-id()"/>
																	</xsl:attribute>
																	<table border="0" cellspacing="5" width="100%">
																		<tr valign="top">
																			<td width="200">
																				<table border="0">
																					<tr>
																						<td class="intitule" width="50">ID</td>
																						<td class="description">
																							<xsl:value-of select="SOURCE_ID"/>
																						</td>
																					</tr>
																					<tr>
																						<td class="intitule" width="50">DATE</td>
																						<td class="description">
																							<xsl:value-of select="Strip_Source/IMAGING_DATE"/>
																						</td>
																					</tr>
																					<tr>
																						<td class="intitule" width="50">TIME</td>
																						<td class="description">
																							<xsl:value-of select="Strip_Source/IMAGING_TIME"/>
																						</td>
																					</tr>
																					<tr>
																						<td class="intitule" width="65">INSTRUMENT</td>
																						<td class="description">
																							<xsl:value-of select="Strip_Source/INSTRUMENT"/>
																							<xsl:value-of select="//Source_Identification/Strip_Source/INSTRUMENT_INDEX"/>
																						</td>
																					</tr>
																				</table>
																			</td>
																		</tr>
																	</table>
																</div>
															</td>
														</tr>
													</xsl:for-each>
												</table>
											</td>
										</tr>
									</table>
									<br/>
								</td>
							</tr>
						</table>
					</div> <!-- /divSources -->
			
					<div id="divCRS" class="masque">
						<br/>
						<table border="0" cellpadding="0" cellspacing="0" width="80%">
							<tr>
								<td valign="middle" align="center">
									<br/>
									<table border="0" cellpadding="0" cellspacing="0" width="100%">
										<tr>
											<td valign="top">
												<table border="0" cellpadding="0" cellspacing="2" width="100%">
													<tr>
														<td>
															<p>
																<span class="entete">Coordinate Reference System</span>
																<hr color="#333366"/>
															</p>
														</td>
													</tr>
												</table>
												<br/>
												<table border="0" cellpadding="0" cellspacing="5" width="100%">
													<!-- Mise en commentaire pour applicabilité à la nouvelle présentation des CRS -->
													<!--tr>
														<td valign="top">
															<p class="intitule">
																<font color="#A9AB87">Horizontal Coordinate System</font>
															</p>
														</td>
														<td></td>
													</tr-->
													<tr>
														<td valign="top">
															<p class="intitule">
																<font color="#A9AB87">Projected Coordinate System</font>
															</p>
														</td>
														<td></td>
													</tr>
													<xsl:if test="//CRS_TABLES">
														<tr>
															<td valign="top">
																<p class="intitule">Geocoding tables identification</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//CRS_TABLES"/>(<xsl:value-of select="//CRS_TABLES/@version"/>)</p>
															</td>
														</tr>
													</xsl:if>
													<xsl:if test="//PROJECTED_CRS_NAME">
														<tr>
															<td valign="top">
																<p class="intitule">Projected Coordinate System name</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//PROJECTED_CRS_NAME"/>
																</p>
															</td>
														</tr>
													</xsl:if>
													<xsl:if test="//PROJECTED_CRS_CODE">
														<tr>
															<td valign="top">
																<p class="intitule">Projected Coordinate System code</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//PROJECTED_CRS_CODE"/>
																</p>
															</td>
														</tr>
													</xsl:if>
													<xsl:if test="//HORIZONTAL_CS_TYPE">
														<tr>
															<td valign="top">
																<p class="intitule">Horizontal Coordinate System type</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//HORIZONTAL_CS_TYPE"/>
																</p>
															</td>
														</tr>
													</xsl:if>
													<xsl:if test="//HORIZONTAL_CS_NAME">
														<tr>
															<td valign="top">
																<p class="intitule">Horizontal coordinate system identification name</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//HORIZONTAL_CS_NAME"/>
																</p>
															</td>
														</tr>
													</xsl:if>
													<!-- Mise en commentaire pour applicabilité à la nouvelle présentation des CRS -->
													<!--tr>
														<td valign="top">
															<p class="intitule">
																<font color="#A9AB87">Geographic Coordinate System</font>
															</p>
														</td>
														<td>
															<p class="description"></p>
														</td>
													</tr-->
													<xsl:if test="//GEOGRAPHIC_CS_NAME">
														<tr>
															<td valign="top">
																<p class="intitule">Geographic Coordinate System</p>
															</td>
															<td>
																<p class="description">
																	<xsl:value-of select="//GEOGRAPHIC_CS_NAME"/>
																</p>
															</td>
														</tr>
													</xsl:if>
												</table>
											</td>
										</tr>
									</table>
									<br/>
								</td>
							</tr>
						</table>
					</div> <!-- /divCRS -->
			
					<div id="divGEO" class="masque">
						<br/>
						<xsl:if test="//ULXMAP">
			
							<table border="0" cellpadding="0" cellspacing="0" width="80%" >
								<tr>
									<td valign="middle" align="center">
										<br/>
										<table border="0" cellpadding="0" cellspacing="0" width="100%">
											<tr>
												<td valign="top">
													<table border="0" cellpadding="0" cellspacing="2" width="100%">
														<tr>
															<td>
																<p>
																	<span class="entete">Geoposition</span>
																	<hr color="#333366"/>
																</p>
															</td>
														</tr>
													</table>
													<br/>
													<table border="0" cellpadding="0" cellspacing="5" width="100%">
														<xsl:if test="//ULXMAP">
															<tr>
																<td valign="top">
																	<p class="intitule">Upper - Left Map X Coordinate</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//ULXMAP"/>
																		<xsl:value-of select="//ULXMAP/@unit"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<xsl:if test="//ULYMAP">
															<tr>
																<td valign="top">
																	<p class="intitule">Upper - Left Map Y Coordinate</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//ULYMAP"/>
																		<xsl:value-of select="//ULXMAP/@unit"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<xsl:if test="//XDIM">
															<tr>
																<td valign="top">
																	<p class="intitule">Image sampling</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//XDIM"/> x <xsl:value-of select="//YDIM"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
													</table>
												</td>
											</tr>
										</table>
										<br/>
									</td>
								</tr>
							</table>
						</xsl:if>
					</div> <!-- /divGEO -->
			
					<div id="divProd" class="affiche">
						<br/>
						<xsl:if test="//Product_Information">
							<table border="0" cellpadding="0" cellspacing="0" width="80%" >
								<tr>
									<td valign="middle" align="center">
										<br/>
										<table border="0" cellpadding="0" cellspacing="0" width="100%">
											<tr>
												<td valign="top">
													<table border="0" cellpadding="0" cellspacing="2" width="100%">
														<tr>
															<td>
																<p>
																	<span class="entete">Production</span>
																	<hr color="#333366"/>
																</p>
															</td>
														</tr>
													</table>
													<br/>
													<table border="0" cellpadding="0" cellspacing="5" width="100%">
														<xsl:if test="//PRODUCTION_DATE">
															<tr>
																<td valign="top">
																	<p class="intitule">Production Date</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//PRODUCTION_DATE"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<xsl:if test="//JOB_ID">
															<tr>
																<td valign="top">
																	<p class="intitule">Job identification</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//JOB_ID"/>
																		<br/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<!--xsl:if test="//PRODUCT_TYPE">
															<tr>
																<td valign="top">
																	<p class="intitule">Product type identification</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//PRODUCT_TYPE"/>
																		<br/>
																	</p>
																</td>
															</tr>
														</xsl:if-->
														<xsl:if test="//PRODUCER_NAME">
															<tr>
																<td valign="top">
																	<p class="intitule">Dataset Producer Identification</p>
																</td>
																<td>
																	<p class="description">
																		<xsl:value-of select="//PRODUCER_NAME"/>
																	</p>
																</td>
															</tr>
														</xsl:if>
														<xsl:if test="//PRODUCER_URL">
															<tr>
																<td valign="top">
																	<p class="intitule">Producer link</p>
																</td>
																<td>
																	<p class="description">
																		<a target="_blank">
																			<xsl:attribute name="href">
																				<xsl:value-of select="//PRODUCER_URL/@href"/>
																			</xsl:attribute>
																			<xsl:value-of select="//PRODUCER_URL/@href"/>
																		</a>
																	</p>
																</td>
															</tr>
														</xsl:if>
													</table>
												</td>
											</tr>
										</table>
										<br/>
									</td>
								</tr>
							</table>
						</xsl:if>
					</div> <!-- /divProd -->
					
					<a name="quicklook"></a>
					<div id="divQuicklook" class="masque">
						<br/>
						<xsl:if test="//DATASET_QL_PATH/@href">
							<table border="0" cellpadding="0" cellspacing="0" width="80%" >
								<tr>
									<td valign="middle" align="center">
										<br/>
										<table border="0" cellpadding="0" cellspacing="0" width="100%">
											<tr>
												<td valign="top">
													<div align="center">
														<table border="0" cellpadding="0" cellspacing="2" width="100%">
															<tr>
																<td>
																	<p>
																		<span class="entete">Quicklook</span>
																		<hr color="#333366"/>
																	</p>
																</td>
															</tr>
														</table>
														<br/>
														<!-- Attention les produits ne sont plus carrés!! -->
														<!--img id="imgQl" width="500" height="500" border="0"-->
														<img id="imgQl" width="500" border="0">
															<xsl:attribute name="src">
																<xsl:value-of select="//DATASET_QL_PATH/@href"/>
															</xsl:attribute>
														</img>
													</div> 
												</td>
											</tr>
										</table>
										<br/>
									</td>
								</tr>
							</table>
						</xsl:if>
					</div> <!-- /divQuicklook -->

					<div id="divCopyright" class="affiche">
						<br/>
						<table border="0" cellpadding="0" cellspacing="0" width="80%" >
							<tr>
								<td valign="middle" align="center">
									<br/>
									<table border="0" cellpadding="0" cellspacing="0" width="100%">
										<tr>
											<td valign="top">
												<table border="0" cellpadding="0" cellspacing="2" width="100%">
													<tr>
														<td>
															<p>
																<span class="entete">Copyright</span>
																<hr color="#333366"/>
															</p>
														</td>
													</tr>
												</table>
												<br/>
												<table border="0" cellpadding="0" cellspacing="5" width="100%">
														<tr>
															<td class="description">
																<xsl:value-of select="//COPYRIGHT"/>
															</td>
														</tr>
													</table>
											</td>
										</tr>
									</table>
									<br/>
								</td>
							</tr>
						</table>
					</div> <!-- /divCopyright -->
					
				</div>
			</body>
		</html>
	</xsl:template>
</xsl:stylesheet>
