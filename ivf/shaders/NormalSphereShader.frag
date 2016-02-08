
void main (void)
{
   vec2 xy = 2.0 * gl_TexCoord[0].st - vec2(1.0, 1.0);
   float r = length(xy);

   float z = sqrt( max( 0.0, 1.0 - r) );
   vec3 N = normalize( vec3( xy, z) );
   vec3 N_color = 0.5 * N + vec3(0.5, 0.5, 0.5);
   float alpha = smoothstep(1.0, 0.99, r);
   gl_FragColor = vec4( N_color, alpha);
}