FasdUAS 1.101.10   ��   ��    k             l     ��  ��    h b In the Music app, export playlists from the "For Export" folder to the Music Library root folder.     � 	 	 �   I n   t h e   M u s i c   a p p ,   e x p o r t   p l a y l i s t s   f r o m   t h e   " F o r   E x p o r t "   f o l d e r   t o   t h e   M u s i c   L i b r a r y   r o o t   f o l d e r .   
  
 l     ��������  ��  ��        l     ����  r         m        �    F o r   E x p o r t  o      ���� 0 
foldername 
folderName��  ��        l    ����  r        m       �   B M e d i a : S h a r e d   M u s i c : M u s i c   L i b r a r y :  o      ���� $0 musiclibraryroot musicLibraryRoot��  ��        l     ��������  ��  ��        l    ����  r         J    
����     o      ���� 0 playlistnames playListNames��  ��     !�� ! l  U "���� " O   U # $ # k   T % %  & ' & l   ��������  ��  ��   '  ( ) ( X    M *�� + * Q   $ H , -�� , k   ' ? . .  / 0 / l  ' , 1 2 3 1 r   ' , 4 5 4 n   ' * 6 7 6 1   ( *��
�� 
pPlP 7 o   ' (���� 0 	aplaylist 	aPlaylist 5 o      ���� 0 p   2 ; 5 The 'try' catches errors here, but why does it fail?    3 � 8 8 j   T h e   ' t r y '   c a t c h e s   e r r o r s   h e r e ,   b u t   w h y   d o e s   i t   f a i l ? 0  9�� 9 Z   - ? : ;���� : =  - 2 < = < n   - 0 > ? > 1   . 0��
�� 
pnam ? o   - .���� 0 p   = o   0 1���� 0 
foldername 
folderName ; r   5 ; @ A @ n   5 8 B C B 1   6 8��
�� 
pnam C o   5 6���� 0 	aplaylist 	aPlaylist A n       D E D  ;   9 : E o   8 9���� 0 playlistnames playListNames��  ��  ��   - R      ������
�� .ascrerr ****      � ****��  ��  ��  �� 0 	aplaylist 	aPlaylist + l    F���� F e     G G 2    ��
�� 
cUsP��  ��   )  H I H l  N N��������  ��  ��   I  J K J l  N N�� L M��   L   log playListNames    M � N N $   l o g   p l a y L i s t N a m e s K  O P O l  N N��������  ��  ��   P  Q R Q l  N N�� S T��   S U O set playListNames to name of every user playlist in folder playlist folderName    T � U U �   s e t   p l a y L i s t N a m e s   t o   n a m e   o f   e v e r y   u s e r   p l a y l i s t   i n   f o l d e r   p l a y l i s t   f o l d e r N a m e R  V W V l  N N��������  ��  ��   W  X�� X X   NT Y�� Z Y l  ^O [ \ ] [ k   ^O ^ ^  _ ` _ l  ^ ^��������  ��  ��   `  a b a r   ^ g c d c l  ^ c e���� e b   ^ c f g f b   ^ a h i h o   ^ _���� $0 musiclibraryroot musicLibraryRoot i o   _ `���� 0 playlistname playListName g m   a b j j � k k 
 . m 3 u 8��  ��   d o      ���� 0 
outputfile 
outputFile b  l m l l  h s n o p n r   h s q r q b   h o s t s m   h k u u � v v  # E X T M 3 U t o   k n��
�� 
ret  r o      ���� 0 atext aText o &   First line of the output file		    p � w w @   F i r s t   l i n e   o f   t h e   o u t p u t   f i l e 	 	 m  x y x l  t t��������  ��  ��   y  z { z r   t � | } | n  t | ~  ~ 2   x |��
�� 
cFlT  4   t x�� �
�� 
cUsP � o   v w���� 0 playlistname playListName } o      ���� 0 	thetracks 	theTracks {  � � � l  � ���������  ��  ��   �  � � � X   � � ��� � � k   � � � �  � � � r   � � � � � n   � � � � � 1   � ���
�� 
psxp � l  � � ����� � e   � � � � n   � � � � � 1   � ���
�� 
pLoc � o   � ����� 0 atrack aTrack��  ��   � o      ���� "0 fileplaceholder filePlaceholder �  � � � l  � ��� � ���   � ; 5 set filePlaceholder to POSIX path of filePlaceholder    � � � � j   s e t   f i l e P l a c e h o l d e r   t o   P O S I X   p a t h   o f   f i l e P l a c e h o l d e r �  � � � r   � � � � � l  � � ����� � e   � � � � n   � � � � � 1   � ���
�� 
pnam � o   � ����� 0 atrack aTrack��  ��   � o      ���� $0 titleplaceholder titlePlaceHolder �  � � � r   � � � � � l  � � ����� � e   � � � � n   � � � � � 1   � ���
�� 
pDur � o   � ����� 0 atrack aTrack��  ��   � o      ���� *0 durationplaceholder durationPlaceHolder �  � � � r   � � � � � I  � ��� � �
�� .sysorondlong        doub � o   � ����� *0 durationplaceholder durationPlaceHolder � �� ���
�� 
dire � m   � ���
�� olierndD��   � o      ���� *0 durationplaceholder durationPlaceHolder �  � � � l  � ��� � ���   �   log durationPlaceHolder    � � � � 0   l o g   d u r a t i o n P l a c e H o l d e r �  � � � r   � � � � � b   � � � � � b   � � � � � b   � � � � � b   � � � � � b   � � � � � b   � � � � � b   � � � � � o   � ����� 0 atext aText � m   � � � � � � �  # E X T I N F : � o   � ����� *0 durationplaceholder durationPlaceHolder � m   � � � � � � �  , � o   � ����� $0 titleplaceholder titlePlaceHolder � o   � ���
�� 
ret  � o   � ����� "0 fileplaceholder filePlaceholder � o   � ���
�� 
ret  � o      ���� 0 atext aText �  ��� � l  � ��� � ���   �  
 log aText    � � � �    l o g   a T e x t��  �� 0 atrack aTrack � o   � ����� 0 	thetracks 	theTracks �  � � � l  � ���������  ��  ��   �  � � � l  � ���������  ��  ��   �  ��� � Q   �O � � � � l  �/ � � � � k   �/ � �  � � � r   � � � � I  ��� � �
�� .rdwropenshor       file � o   � ����� 0 
outputfile 
outputFile � �� ���
�� 
perm � m   � ���
�� boovtrue��   � o      ���� 0 filereference fileReference �  � � � I �� � �
�� .rdwrseofnull���     **** � o  	���� 0 filereference fileReference � �� ��
�� 
set2 � m  �~�~  �   �  � � � l ' � � � � I '�} � �
�} .rdwrwritnull���     **** � o  �|�| 0 atext aText � �{ � �
�{ 
refn � o  �z�z 0 filereference fileReference � �y ��x
�y 
as   � m  !�w
�w 
utf8�x   �   EDITED    � � � �    E D I T E D �  ��v � I (/�u ��t
�u .rdwrclosnull���     **** � o  (+�s�s 0 filereference fileReference�t  �v   �   write text to text file    � � � � 0   w r i t e   t e x t   t o   t e x t   f i l e � R      �r�q�p
�r .ascrerr ****      � ****�q  �p   � Q  7O � ��o � I :F�n ��m
�n .rdwrclosnull���     **** � 4  :B�l �
�l 
file � o  >A�k�k 0 
outputfile 
outputFile�m   � R      �j�i�h
�j .ascrerr ****      � ****�i  �h  �o  ��   \ !  folder playlist folderName    ] � � � 6   f o l d e r   p l a y l i s t   f o l d e r N a m e�� 0 playlistname playListName Z o   Q R�g�g 0 playlistnames playListNames��   $ m     � ��                                                                                      @ alis    ,  Macintosh HD               ���BD ����	Music.app                                                      �������        ����  
 cu             Applications   /:System:Applications:Music.app/   	 M u s i c . a p p    M a c i n t o s h   H D  System/Applications/Music.app   / ��  ��  ��  ��       �f � �   � � � � � �e�d�c�b�a�`�f   � �_�^�]�\�[�Z�Y�X�W�V�U�T�S�R�Q�P
�_ .aevtoappnull  �   � ****�^ 0 
foldername 
folderName�] $0 musiclibraryroot musicLibraryRoot�\ 0 playlistnames playListNames�[ 0 p  �Z 0 
outputfile 
outputFile�Y 0 atext aText�X 0 	thetracks 	theTracks�W "0 fileplaceholder filePlaceholder�V $0 titleplaceholder titlePlaceHolder�U *0 durationplaceholder durationPlaceHolder�T 0 filereference fileReference�S  �R  �Q  �P   � �O�N�M�L
�O .aevtoappnull  �   � **** k    U        !�K�K  �N  �M   �J�I�H�J 0 	aplaylist 	aPlaylist�I 0 playlistname playListName�H 0 atrack aTrack - �G �F�E ��D�C�B�A�@�?�>�=�< j�; u�:�9�8�7�6�5�4�3�2�1�0�/�. � ��-�,�+�*�)�(�'�&�%�$�#�"�G 0 
foldername 
folderName�F $0 musiclibraryroot musicLibraryRoot�E 0 playlistnames playListNames
�D 
cUsP
�C 
kocl
�B 
cobj
�A .corecnte****       ****
�@ 
pPlP�? 0 p  
�> 
pnam�=  �<  �; 0 
outputfile 
outputFile
�: 
ret �9 0 atext aText
�8 
cFlT�7 0 	thetracks 	theTracks
�6 
pLoc
�5 
psxp�4 "0 fileplaceholder filePlaceholder�3 $0 titleplaceholder titlePlaceHolder
�2 
pDur�1 *0 durationplaceholder durationPlaceHolder
�0 
dire
�/ olierndD
�. .sysorondlong        doub
�- 
perm
�, .rdwropenshor       file�+ 0 filereference fileReference
�* 
set2
�) .rdwrseofnull���     ****
�( 
refn
�' 
as  
�& 
utf8�% 
�$ .rdwrwritnull���     ****
�# .rdwrclosnull���     ****
�" 
file�LV�E�O�E�OjvE�O�E ;*�-E[��l 	kh   ��,E�O��,�  ��,�6FY hW X  h[OY��O�[��l 	kh á%�%E` Oa _ %E` O*�/a -E` O p_ [��l 	kh �a ,Ea ,E` O��,EE` O�a ,EE` O_ a a l E` O_ a %_ %a  %_ %_ %_ %_ %E` OP[OY��O >_ a !el "E` #O_ #a $jl %O_ a &_ #a 'a (a ) *O_ #j +W X   *a ,_ /j +W X  h[OY�	U � �!	�! 	  
� ����������
 �  1 9 7 0 - 1 9 9 5 �  B e d t i m e �  C h r i s t m a s �  S M P   1 3   J u n e   2 6 �  S M P   2 7   S e p t   2 5�   �  �  �  �  �  �  �  �  �  �   �  ���  ����
� 
cSrc� =
� kfrmID  
� 
cFoP�\B
� kfrmID   � � h M e d i a : S h a r e d   M u s i c : M u s i c   L i b r a r y : S M P   2 7   S e p t   2 5 . m 3 u 8 � �� # E X T M 3 U  # E X T I N F : 6 4 4 , S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   1 .   A n d a n t e   M a   N o n   T r o p p o ,   A l l e g r o   E n e r g i c o  / V o l u m e s / M e d i a / S h a r e d   M u s i c / M u s i c   L i b r a r y / V i e n n a   P h i l h a r m o n i c   O r c h e s t r a / S i b e l i u s _   S y m p h o n i e s   N o s .   1   &   4 / 1 - 0 1   S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   1 .   A n d a n t e   M a   N o n   T r o p p o ,   A l l e g r o   E n e r g i c o . m 4 a  # E X T I N F : 5 1 6 , S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   2 .   A n d a n t e  / V o l u m e s / M e d i a / S h a r e d   M u s i c / M u s i c   L i b r a r y / V i e n n a   P h i l h a r m o n i c   O r c h e s t r a / S i b e l i u s _   S y m p h o n i e s   N o s .   1   &   4 / 1 - 0 2   S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   2 .   A n d a n t e . m 4 a  # E X T I N F : 2 9 7 , S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   3 .   S c h e r z o :   A l l e g r o  / V o l u m e s / M e d i a / S h a r e d   M u s i c / M u s i c   L i b r a r y / V i e n n a   P h i l h a r m o n i c   O r c h e s t r a / S i b e l i u s _   S y m p h o n i e s   N o s .   1   &   4 / 1 - 0 3   S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   3 .   S c h e r z o _   A l l e g r o . m 4 a  # E X T I N F : 7 1 5 , S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   4 .   F i n a l e :   Q u a s i   U n a   F a n t a s i a  / V o l u m e s / M e d i a / S h a r e d   M u s i c / M u s i c   L i b r a r y / V i e n n a   P h i l h a r m o n i c   O r c h e s t r a / S i b e l i u s _   S y m p h o n i e s   N o s .   1   &   4 / 1 - 0 4   S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   4 .   F i n a l e _   Q u a s i   U n a   F a n t a s i a . m 4 a  � ��     ��� ��
�	  ����
� 
cSrc� =
� kfrmID  
� 
cUsP�
e.
�	 kfrmID  
� 
cFlT�gt
� kfrmID      !���! "��� "  �������
�� 
cSrc�� =
�� kfrmID  
� 
cUsP�e.
�  kfrmID  
� 
cFlT�gs
� kfrmID   ## $������$ %������%  �������
�� 
cSrc�� =
�� kfrmID  
�� 
cUsP��e.
�� kfrmID  
�� 
cFlT��gr
�� kfrmID   && '������' (������(  �������
�� 
cSrc�� =
�� kfrmID  
�� 
cUsP��e.
�� kfrmID  
�� 
cFlT��gq
�� kfrmID    �))d / V o l u m e s / M e d i a / S h a r e d   M u s i c / M u s i c   L i b r a r y / V i e n n a   P h i l h a r m o n i c   O r c h e s t r a / S i b e l i u s _   S y m p h o n i e s   N o s .   1   &   4 / 1 - 0 4   S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   4 .   F i n a l e _   Q u a s i   U n a   F a n t a s i a . m 4 a �** � S y m p h o n y   N o .   1   I n   E   M i n o r ,   O p .   3 9   -   4 .   F i n a l e :   Q u a s i   U n a   F a n t a s i a�e��d R�c  �b  �a  �`   ascr  ��ޭ