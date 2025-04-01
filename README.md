This code is used to filter a list of molecules in html format based on their dipole moment, quadrupole moment, number of atoms and melting temperature. A total of 5 filters are applied: 
1. Filter0 --> removes ions, dimers, trimers and tetramers from the originally html file and returns the output as csv. Since the html file contains vibrations and not molecules, the duplicated names are removed as well
3. Filter1 --> filters molecules by dipole moment
4. Filter2 --> filters molecules by quadrupole moment
5. Filter3 --> filter molecules by the number of atoms
6. Filter4 --> filter molecules by their melting temperature present in wikipedia


You can get the code by: 
git clone https://https://github.com/mirelae97/molecule_filtration
