<?xml version="1.0"?>
<!-- 
Description : Stylesheet for Pleiades volumes
Version : 5.0.1
DIT 26407: Evolution du DIMAP V2 avec les nouvelles nomenclatures Astrium Services / SPOT IMAGE dans les labels et les Copyright
DIT 26997: Correction de la prise en compte d'un produit multi-volume + de la documentation
FA OGM 14640 : Correction sur la régression de la prise en compte des produits multi volumes (mono volume non traite!)
DIT 32740: DIMAP Format Rebranding (nouvelle marque AIRBUS)
-->
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:gmd="http://www.isotc211.org/2005/gmd" xmlns:gml="http://www.opengis.net/gml" xmlns:gmx="http://www.isotc211.org/2005/gmx" xmlns:gsr="http://www.isotc211.org/2005/gsr" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:gss="http://www.isotc211.org/2005/gss" xmlns:gts="http://www.isotc211.org/2005/gts" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:gco="http://www.isotc211.org/2005/gco">
	<xsl:template match="/">
		<HTML height="100%">
			<HEAD>
				<TITLE>
					<xsl:value-of select="//DATASET_NAME"/>
				</TITLE>
				<script language="javascript">
        function detail(p) {
          window.status = p;
          document.getElementById("details").src = p;
        }
        function ViewQL(path) {
          window.open(path, "QL", "toolbars=no, scrollbars=yes");
        }
      </script>
			</HEAD>
			<!-- Fond d'image change en blanc -->
			<BODY height="100%">
				<table width="100%" height="100%" border="0" cellpadding="0" cellspacing="0">
					<TABLE WIDTH="100%" BORDER="0" CELLPADDING="0" CELLSPACING="0" STYLE="page-break-inside: avoid">
						<TR>
							<TD WIDTH="300 px">
								<A>
									<xsl:attribute name="HREF">http://www.geo-airbusds.com</xsl:attribute>
									<IMG WIDTH="250" BORDER="0" src="LIBRARY/LOGO.JPG" alt="AIRBUS DS GEO"/>
								</A>
							</TD>
							<TD VALIGN="TOP">
								<P>
									<FONT FACE="Arial" STYLE="font-size: 12pt; font-weight: bold;text-decoration: underline;color: #333366">
										<xsl:value-of select="//DATASET_NAME"/>
										<xsl:text> of </xsl:text>
										<xsl:value-of select="//DATASET_ID"/>
										<BR/>
										<BR/>
									</FONT>
									<FONT FACE="Arial" STYLE="font-size: 10 pt;">
                Production: 
               </FONT>
									<FONT FACE="Arial" STYLE="font-size: 10 pt;">
										<A>
											<xsl:attribute name="href">http://www.geo-airbusds.com/</xsl:attribute>
											<xsl:value-of select="//PRODUCER_NAME"/>
										</A>
										<BR/>
				      Date : <xsl:value-of select="//PRODUCTION_DATE"/>
										<BR/>
									</FONT>
								</P>
							</TD>
						</TR>
					</TABLE>
					<HR color="#FF5601"/>
					<TABLE WIDTH="100%" HEIGHT="100%">
						<BR/>
						<TR>
							<TD WIDTH="20%" HEIGHT="100%" VALIGN="TOP">
								<TABLE border="0">
								<!-- OGM 14640 - Choix selon produit mono ou multi volume -->
								<xsl:choose>
								<!-- Produit multi volume -->
									<xsl:when test="//Volume">
										<!-- Selection du volume courant -->
										<xsl:for-each select="//Volume[VOLUME_INDEX/@current='true']">
											<xsl:for-each select="./Dataset_Content/Dataset_Components/Component">
												<xsl:variable name="Producthref" select="COMPONENT_TN_PATH/@href"/>
												<!-- Selection des produits image seulement -->
												<xsl:if test="starts-with($Producthref,'IMG')">
													<TR>
														<TD rowspan="3">
															<A>
																<xsl:attribute name="href">javascript:detail('./<xsl:value-of select="substring-before($Producthref,'/')"/>/INDEX.HTM')</xsl:attribute>
																<IMG BORDER="0" WIDTH="90" ALT="Click to display additional information">
																	<xsl:attribute name="src"><xsl:value-of select="$Producthref"/></xsl:attribute>
																</IMG>
															</A>
														</TD>
														<TD>
															<font size="2pt">
																<A>
																	<font face="Arial" size="2pt">
																		<xsl:value-of select="substring-before($Producthref,'/')"/> :
																</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font size="2pt">
																<A>
																	<xsl:attribute name="href">javascript:detail('./<xsl:value-of select="substring-before($Producthref,'/')"/>/INDEX.HTM')</xsl:attribute>
																	<font face="Arial" size="1pt">
																		<xsl:value-of select="COMPONENT_TITLE"/>
																	</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font face="Arial" size="1pt">(<xsl:value-of select="COMPONENT_TITLE"/>)</font>
														</TD>
													</TR>
													<TD colspan="2">
														<BR/>
													</TD>
												</xsl:if>
												<!-- Insertion du lien vers la documentation -->
												<xsl:variable name="Doctitle" select="COMPONENT_TITLE"/>
												<!-- Selection de la documentation seulement -->
												<xsl:if test="starts-with($Doctitle,'Digi')">
													<TR>
														<TD rowspan="3">
															<A>
																<xsl:attribute name="href">javascript:detail('<xsl:value-of select="COMPONENT_PATH/@href"/>')</xsl:attribute>
																<IMG BORDER="0" WIDTH="90" ALT="Click to display additional information">
																	<xsl:attribute name="src"><xsl:value-of select="COMPONENT_TN_PATH/@href"/></xsl:attribute>
																</IMG>
															</A>
														</TD>
														<TD>
															<font size="2pt">
																<A>
																	<font face="Arial" size="2pt">
																		<xsl:value-of select="COMPONENT_TITLE"/> :
																</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font size="2pt">
																<A>
																	<xsl:attribute name="href">javascript:detail('<xsl:value-of select="COMPONENT_PATH/@href"/>')</xsl:attribute>
																	<font face="Arial" size="1pt">
																		<xsl:value-of select="COMPONENT_TITLE"/>
																	</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font face="Arial" size="1pt">(<xsl:value-of select="COMPONENT_TITLE"/>)</font>
														</TD>
													</TR>
													<TD colspan="2">
														<BR/>
													</TD>
												</xsl:if>
											</xsl:for-each>
										</xsl:for-each>
									</xsl:when>
									<!-- Produit mono volume -->
									<xsl:otherwise>
											<xsl:for-each select="//Component">
												<xsl:variable name="Producthref" select="COMPONENT_TN_PATH/@href"/>
												<!-- Selection des produits image seulement -->
												<xsl:if test="starts-with($Producthref,'IMG')">
													<TR>
														<TD rowspan="3">
															<A>
																<xsl:attribute name="href">javascript:detail('./<xsl:value-of select="substring-before($Producthref,'/')"/>/INDEX.HTM')</xsl:attribute>
																<IMG BORDER="0" WIDTH="90" ALT="Click to display additional information">
																	<xsl:attribute name="src"><xsl:value-of select="$Producthref"/></xsl:attribute>
																</IMG>
															</A>
														</TD>
														<TD>
															<font size="2pt">
																<A>
																	<font face="Arial" size="2pt">
																		<xsl:value-of select="substring-before($Producthref,'/')"/> :
																</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font size="2pt">
																<A>
																	<xsl:attribute name="href">javascript:detail('./<xsl:value-of select="substring-before($Producthref,'/')"/>/INDEX.HTM')</xsl:attribute>
																	<font face="Arial" size="1pt">
																		<xsl:value-of select="COMPONENT_TITLE"/>
																	</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font face="Arial" size="1pt">(<xsl:value-of select="COMPONENT_TITLE"/>)</font>
														</TD>
													</TR>
													<TD colspan="2">
														<BR/>
													</TD>
												</xsl:if>
												<!-- Insertion du lien vers la documentation -->
												<xsl:variable name="Doctitle" select="COMPONENT_TITLE"/>
												<!-- Selection de la documentation seulement -->
												<xsl:if test="starts-with($Doctitle,'Digi')">
													<TR>
														<TD rowspan="3">
															<A>
																<xsl:attribute name="href">javascript:detail('<xsl:value-of select="COMPONENT_PATH/@href"/>')</xsl:attribute>
																<IMG BORDER="0" WIDTH="90" ALT="Click to display additional information">
																	<xsl:attribute name="src"><xsl:value-of select="COMPONENT_TN_PATH/@href"/></xsl:attribute>
																</IMG>
															</A>
														</TD>
														<TD>
															<font size="2pt">
																<A>
																	<font face="Arial" size="2pt">
																		<xsl:value-of select="COMPONENT_TITLE"/> :
																</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font size="2pt">
																<A>
																	<xsl:attribute name="href">javascript:detail('<xsl:value-of select="COMPONENT_PATH/@href"/>')</xsl:attribute>
																	<font face="Arial" size="1pt">
																		<xsl:value-of select="COMPONENT_TITLE"/>
																	</font>
																</A>
															</font>
														</TD>
													</TR>
													<TR>
														<TD>
															<font face="Arial" size="1pt">(<xsl:value-of select="COMPONENT_TITLE"/>)</font>
														</TD>
													</TR>
													<TD colspan="2">
														<BR/>
													</TD>
												</xsl:if>
											</xsl:for-each>
									</xsl:otherwise>
								</xsl:choose>
								</TABLE>
							</TD>
							<TD WIDTH="60%" HEIGHT="100%" VALIGN="TOP">
								<IFRAME frameborder="1" WIDTH="100%" HEIGHT="100%" ID="details"/>
							</TD>
						</TR>
					</TABLE>
				</table>
			</BODY>
		</HTML>
	</xsl:template>
</xsl:stylesheet>
